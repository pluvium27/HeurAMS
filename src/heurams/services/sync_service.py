# WebDAV 同步服务
import hashlib
import os
import pathlib
import time
import typing
from dataclasses import dataclass
from enum import Enum

import requests
from webdav3.client import Client

from heurams.context import config_var
from heurams.services.logger import get_logger

logger = get_logger(__name__)


class SyncMode(Enum):
    """同步模式枚举"""
    BIDIRECTIONAL = "bidirectional"
    UPLOAD_ONLY = "upload_only"
    DOWNLOAD_ONLY = "download_only"


class ConflictStrategy(Enum):
    """冲突解决策略枚举"""
    NEWER = "newer"  # 较新文件覆盖较旧文件
    ASK = "ask"  # 用户手动选择
    KEEP_BOTH = "keep_both"  # 保留双方（重命名）


@dataclass
class SyncConfig:
    """同步配置数据类"""
    enabled: bool = False
    url: str = ""
    username: str = ""
    password: str = ""
    remote_path: str = "/heurams/"
    sync_mode: SyncMode = SyncMode.BIDIRECTIONAL
    conflict_strategy: ConflictStrategy = ConflictStrategy.NEWER
    verify_ssl: bool = True


class SyncService:
    """WebDAV 同步服务"""

    def __init__(self, config):
        self.config = config
        logger.debug(f"{str(self.config)}")
        self.client = None
        self._setup_client()

    def _setup_client(self):
        """设置 WebDAV 客户端"""
        if not self.config.enabled or not self.config.url:
            logger.warning("同步服务未启用或未配置 URL")
            return

        options = {
            'webdav_hostname': self.config.url,
            'webdav_login': self.config.username,
            'webdav_password': self.config.password,
            'webdav_root': self.config.remote_path,
            'verify_ssl': self.config.verify_ssl,
            'disable_check': True,  # 不检查服务器支持的功能
        }

        try:
            self.client = Client(options)
            logger.info("WebDAV 客户端初始化完成")
        except Exception as e:
            logger.error("WebDAV 客户端初始化失败: %s", e)
            self.client = None

    def test_connection(self) -> bool:
        """测试 WebDAV 服务器连接"""
        if not self.client:
            logger.error("WebDAV 客户端未初始化")
            return False

        try:
            # 尝试列出根目录
            self.client.list()
            logger.info("WebDAV 连接测试成功")
            return True
        except Exception as e:
            logger.error("WebDAV 连接测试失败: %s", e)
            return False

    def _get_local_files(self, local_dir: pathlib.Path) -> typing.Dict[str, dict]:
        """获取本地文件列表及其元数据"""
        files = {}
        for root, _, filenames in os.walk(local_dir):
            for filename in filenames:
                file_path = pathlib.Path(root) / filename
                rel_path = file_path.relative_to(local_dir)
                stat = file_path.stat()
                files[str(rel_path)] = {
                    'path': file_path,
                    'size': stat.st_size,
                    'mtime': stat.st_mtime,
                    'hash': self._calculate_hash(file_path),
                }
        return files

    def _get_remote_files(self) -> typing.Dict[str, dict]:
        """获取远程文件列表及其元数据"""
        if not self.client:
            return {}

        try:
            remote_list = self.client.list(recursive=True)
            files = {}
            for item in remote_list:
                if not item.endswith('/'):  # 忽略目录
                    rel_path = item.lstrip('/')
                    try:
                        info = self.client.info(item)
                        files[rel_path] = {
                            'path': item,
                            'size': info.get('size', 0),
                            'mtime': self._parse_remote_mtime(info),
                        }
                    except Exception as e:
                        logger.warning("无法获取远程文件信息 %s: %s", item, e)
            return files
        except Exception as e:
            logger.error("获取远程文件列表失败: %s", e)
            return {}

    def _calculate_hash(self, file_path: pathlib.Path, block_size: int = 65536) -> str:
        """计算文件的 SHA-256 哈希值"""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for block in iter(lambda: f.read(block_size), b''):
                    sha256.update(block)
            return sha256.hexdigest()
        except Exception as e:
            logger.error("计算文件哈希失败 %s: %s", file_path, e)
            return ""

    def _parse_remote_mtime(self, info: dict) -> float:
        """解析远程文件的修改时间"""
        # WebDAV 可能返回 Last-Modified 头或其他时间格式
        # 这里简单返回当前时间，实际应根据服务器响应解析
        return time.time()

    def sync_directory(self, local_dir: pathlib.Path) -> typing.Dict[str, typing.Any]:
        """
        同步目录
        
        Args:
            local_dir: 本地目录路径
            
        Returns:
            同步结果统计
        """
        if not self.client:
            logger.error("WebDAV 客户端未初始化")
            return {'success': False, 'error': '客户端未初始化'}

        results = {
            'uploaded': 0,
            'downloaded': 0,
            'conflicts': 0,
            'errors': 0,
            'success': True,
        }

        try:
            # 确保远程目录存在
            self.client.mkdir(self.config.remote_path)

            local_files = self._get_local_files(local_dir)
            remote_files = self._get_remote_files()

            # 根据同步模式处理文件
            if self.config.sync_mode in [SyncMode.BIDIRECTIONAL, SyncMode.UPLOAD_ONLY]:
                stats = self._upload_files(local_dir, local_files, remote_files)
                results['uploaded'] += stats.get('uploaded', 0)
                results['conflicts'] += stats.get('conflicts', 0)
                results['errors'] += stats.get('errors', 0)

            if self.config.sync_mode in [SyncMode.BIDIRECTIONAL, SyncMode.DOWNLOAD_ONLY]:
                stats = self._download_files(local_dir, local_files, remote_files)
                results['downloaded'] += stats.get('downloaded', 0)
                results['conflicts'] += stats.get('conflicts', 0)
                results['errors'] += stats.get('errors', 0)

            logger.info("同步完成: %s", results)
            return results

        except Exception as e:
            logger.error("同步过程中发生错误: %s", e)
            results['success'] = False
            results['error'] = str(e)
            return results

    def _upload_files(self, local_dir: pathlib.Path, 
                     local_files: dict, remote_files: dict) -> typing.Dict[str, int]:
        """上传文件到远程服务器"""
        stats = {'uploaded': 0, 'errors': 0, 'conflicts': 0}
        
        for rel_path, local_info in local_files.items():
            remote_info = remote_files.get(rel_path)
            
            # 判断是否需要上传
            should_upload = False
            conflict_resolved = False
            remote_path = os.path.join(self.config.remote_path, rel_path)
            
            if not remote_info:
                should_upload = True  # 远程不存在
            else:
                # 检查冲突
                local_mtime = local_info.get('mtime', 0)
                remote_mtime = remote_info.get('mtime', 0)
                
                if local_mtime != remote_mtime:
                    # 存在冲突
                    stats['conflicts'] += 1
                    should_upload, should_download = self._handle_conflict(local_info, remote_info)
                    
                    if should_upload and self.config.conflict_strategy == ConflictStrategy.KEEP_BOTH:
                        # 重命名远程文件避免覆盖
                        conflict_suffix = f".conflict_{int(remote_mtime)}"
                        name, ext = os.path.splitext(rel_path)
                        new_rel_path = f"{name}{conflict_suffix}{ext}" if ext else f"{name}{conflict_suffix}"
                        remote_path = os.path.join(self.config.remote_path, new_rel_path)
                        conflict_resolved = True
                        logger.debug("冲突文件重命名: %s -> %s", rel_path, new_rel_path)
                else:
                    # 时间相同，无需上传
                    should_upload = False
            
            if should_upload:
                try:
                    self.client.upload_file(local_info['path'], remote_path)
                    stats['uploaded'] += 1
                    logger.debug("上传文件: %s -> %s", rel_path, remote_path)
                except Exception as e:
                    logger.error("上传文件失败 %s: %s", rel_path, e)
                    stats['errors'] += 1
        
        return stats

    def _download_files(self, local_dir: pathlib.Path,
                       local_files: dict, remote_files: dict) -> typing.Dict[str, int]:
        """从远程服务器下载文件"""
        stats = {'downloaded': 0, 'errors': 0, 'conflicts': 0}
        
        for rel_path, remote_info in remote_files.items():
            local_info = local_files.get(rel_path)
            
            # 判断是否需要下载
            should_download = False
            if not local_info:
                should_download = True  # 本地不存在
            else:
                # 检查冲突
                local_mtime = local_info.get('mtime', 0)
                remote_mtime = remote_info.get('mtime', 0)
                
                if local_mtime != remote_mtime:
                    # 存在冲突
                    stats['conflicts'] += 1
                    should_upload, should_download = self._handle_conflict(local_info, remote_info)
                    # 如果应该上传，则不应该下载（冲突已在上传侧处理）
                    if should_upload:
                        should_download = False
                else:
                    # 时间相同，无需下载
                    should_download = False
            
            if should_download:
                try:
                    local_path = local_dir / rel_path
                    local_path.parent.mkdir(parents=True, exist_ok=True)
                    self.client.download_file(remote_info['path'], str(local_path))
                    stats['downloaded'] += 1
                    logger.debug("下载文件: %s -> %s", rel_path, local_path)
                except Exception as e:
                    logger.error("下载文件失败 %s: %s", rel_path, e)
                    stats['errors'] += 1
        
        return stats

    def _handle_conflict(self, local_info: dict, remote_info: dict) -> typing.Tuple[bool, bool]:
        """
        处理文件冲突
        
        Returns:
            (should_upload, should_download) - 是否应该上传和下载
        """
        local_mtime = local_info.get('mtime', 0)
        remote_mtime = remote_info.get('mtime', 0)
        
        if self.config.conflict_strategy == ConflictStrategy.NEWER:
            # 较新文件覆盖较旧文件
            if local_mtime > remote_mtime:
                return True, False  # 上传本地较新版本
            elif remote_mtime > local_mtime:
                return False, True  # 下载远程较新版本
            else:
                return False, False  # 时间相同，无需操作
        
        elif self.config.conflict_strategy == ConflictStrategy.KEEP_BOTH:
            # 保留双方 - 重命名远程文件
            # 这里实现简单的重命名策略：添加冲突后缀
            # 实际应该在上传时处理重命名
            # 返回 True, False 表示上传重命名后的文件
            # 重命名逻辑在调用处处理
            return True, False
        
        elif self.config.conflict_strategy == ConflictStrategy.ASK:
            # 用户手动选择 - 记录冲突，跳过
            # 返回 False, False 跳过，等待用户决定
            logger.warning("文件冲突需要用户手动选择: local_mtime=%s, remote_mtime=%s", 
                          local_mtime, remote_mtime)
            return False, False
        
        return False, False

    def _should_upload(self, local_info: dict, remote_info: dict) -> bool:
        """判断是否需要上传（本地较新或哈希不同）"""
        # 这里实现简单的基于时间的比较
        # 实际应该使用哈希比较更可靠
        return local_info.get('mtime', 0) > remote_info.get('mtime', 0)

    def _should_download(self, local_info: dict, remote_info: dict) -> bool:
        """判断是否需要下载（远程较新）"""
        return remote_info.get('mtime', 0) > local_info.get('mtime', 0)

    def upload_file(self, local_path: pathlib.Path, remote_path: str = "") -> bool:
        """上传单个文件"""
        if not self.client:
            return False

        try:
            if not remote_path:
                remote_path = os.path.join(self.config.remote_path, local_path.name)
            self.client.upload_file(str(local_path), remote_path)
            logger.info("文件上传成功: %s -> %s", local_path, remote_path)
            return True
        except Exception as e:
            logger.error("文件上传失败: %s", e)
            return False

    def download_file(self, remote_path: str, local_path: pathlib.Path) -> bool:
        """下载单个文件"""
        if not self.client:
            return False

        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            self.client.download_file(remote_path, str(local_path))
            logger.info("文件下载成功: %s -> %s", remote_path, local_path)
            return True
        except Exception as e:
            logger.error("文件下载失败: %s", e)
            return False

    def delete_remote_file(self, remote_path: str) -> bool:
        """删除远程文件"""
        if not self.client:
            return False

        try:
            self.client.clean(remote_path)
            logger.info("远程文件删除成功: %s", remote_path)
            return True
        except Exception as e:
            logger.error("远程文件删除失败: %s", e)
            return False


def create_sync_service_from_config() -> typing.Optional[SyncService]:
    """从配置文件创建同步服务实例"""
    try:
        from heurams.context import config_var
        
        sync_config = config_var.get()['providers']['sync']['webdav']
        if not sync_config.get('enabled', False):
            logger.debug("同步服务未启用")
            return None
        
        config = SyncConfig(
            enabled=sync_config.get('enabled', False),
            url=sync_config.get('url', ''),
            username=sync_config.get('username', ''),
            password=sync_config.get('password', ''),
            remote_path=sync_config.get('remote_path', '/heurams/'),
            sync_mode=SyncMode(sync_config.get('sync_mode', 'bidirectional')),
            conflict_strategy=ConflictStrategy(sync_config.get('conflict_strategy', 'newer')),
            verify_ssl=sync_config.get('verify_ssl', True),
        )
        
        service = SyncService(config)
        if service.client is None:
            logger.warning("同步服务客户端创建失败")
            return None
            
        return service
        
    except Exception as e:
        logger.error("创建同步服务失败: %s", e)
        return None