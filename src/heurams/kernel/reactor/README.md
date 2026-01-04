# Reactor - 记忆流程状态机模块
Reactor 是 HeurAMS 的记忆流程状态机模块, 和界面 (interface) 的实现是解耦的, 以便后期与其他框架的适配.  
得益于 Pickle, 状态机模块支持快照!  
## Phaser - 全局阶段控制器
在一次队列记忆流程中, Phaser 代表记忆流程本身.  
### 属性
#### 状态属性
其有状态属性:
- unsure - 用于初始化
- *quick_review - 复习逾期的单元
- *recognition - 辨识新单元
- *final_review - 复习所有逾期的和新辨认的单元
- finished  - 表示完成 
> 逾期的: 指 SM-2 算法间隔显示应该复习的单元

带 * 的属性表示实际的记忆阶段, 由 repo 中 schedule.toml 中 schedule 列表显式声明, 运行过程中可以选择性执行, "空的" Procession 会被直接跳过.

在初始化 Procession 时, 每个 Procession 被赋予一个不重复的状态属性 作为"阶段状态"属性, 以此标识 Procession 的阶段属性, 因为每个 Procession 管理一个阶段下的复习进程.  

你可以用 state 属性获取 Phaser 的当前状态.
#### Procession 属性
储存一个顺序列表, 保存所有构造的 Procession.  
顺序与 repo 中 schedule.toml 中 schedule 列表中的顺序完全相同

### 初始化
Phaser 接受一个存储 Atom 对象的列表, 作为组织记忆流程的材料  
在内部, 根据是否激活将其分为 new_atoms 与 old_atoms.  
因此, 如果你传入的列表中有算法上"无所事事"的 Atom, 流程会对其进行"加强复习"
由此创建 Procession.  

### 直接输出呈现形式
Phaser 的 __repr__ 定义了此对象"官方的显示"用作直观的调试.  
其以 ascii 表格形式输出, 格式也符合 markdown 表格规范, 你可以直接复制到 markdown.  
示例:
```text
| Type   | State   | Processions            | Current Procession   |
|:-------|:--------|:-----------------------|:---------------------|
| Phaser | unsure  | ['新记忆', '总体复习'] | 新记忆               |
```
| Type   | State   | Processions            | Current Procession   |
|:-------|:--------|:-----------------------|:---------------------|
| Phaser | unsure  | ['新记忆', '总体复习'] | 新记忆               |

### 方法
作为一个 Transition Machine 对象的继承, 其拥有 Machine 对象拥有的所有方法.  
除此之外, 它也拥有一些其他方法.  
#### current_procession(self)
用于查询当前的 Procession, 并且根据当前 Procession 更新自身状态.  
返回一个 Procession 对象, 是当前阶段的 Procession.  
内部运作是返回第一个状态不为 finished 的 Procession, 并将自身状态变更为 Procession 的"阶段状态"属性  
若所有 Procession 都已完成, 将返回一个"阶段状态"为 finished 的 Procession 占位符对象(它不在 procession 属性中), 并更新自身状态为 finished.

## Procession - 阶段管理器
### 属性
#### 状态属性
其有状态属性:
- active - 标识未完成, 初始化的默认属性
- finished - 完成了
#### 其他属性
- current_atom: 当前记忆原子的引用
- atoms: 队列中所有原子列表
- cursor: 指针, 是当前原子在 atoms 列表中的索引
- phase: "阶段属性"
> 注意区分 "Phaser" 和 "Phase", 其中 "Phase" 表示 "Phaser State".
- name_: 阶段的命名
- state: 当前状态属性
### 初始化
接受一个 atoms 列表与 phase_state (PhaserState Enum 类型)对象
### 直接输出呈现形式
同 Phaser, 但显示数据有所不同  
与 Phaser 不同, Procession 显示队列会对过长的 atom.ident 进行缩略(末尾 `>` 符号)
```text
| Type       | Name   | State   | Progress   | Queue                  | Current Atom                  |
|:-----------|:-------|:--------|:-----------|:-----------------------|:------------------------------|
| Procession | 新记忆 | active  | 1 / 2      | ['秦孝公>', '君臣固>'] | 秦孝公据崤函之固, 拥雍州之地, |
```
| Type       | Name   | State   | Progress   | Queue                  | Current Atom                  |
|:-----------|:-------|:--------|:-----------|:-----------------------|:------------------------------|
| Procession | 新记忆 | active  | 1 / 2      | ['秦孝公>', '君臣固>'] | 秦孝公据崤函之固, 拥雍州之地, |
### 方法
作为一个 Transition Machine 对象的继承, 其拥有 Machine 对象拥有的所有方法.  
除此之外, 它也拥有一些其他方法.  
#### forward(self, step=1)
移动 cursor 并依情况更新 current_atom 和状态属性  
无论 Procession 是否处于完成状态, forward 操作都是可逆的, 你可以传入负数, 此时已完成的 Procession 会自动"重启".  

#### append(self, atom=None)
追加(回忆失败的)原子(默认为当前原子, 传入 None 会自动转化为当前原子)到队列末端  
如果这个原子已经处于队列末端, 不会重复追加, 除非队列只剩下这个原子还没完成(此时最多重复两个)

#### process(self)
返回 cursor 值

#### __len__(self)
返回剩余原子量(而不是原子总量)  
可以使用 len 函数调用
获取原子总量请用 len(obj.atoms), 或者 total_length(self) 方法

#### total_length(self)
返回队列原子总量

#### is_empty(self)
判断是否为空队列(传入原子列表对象是空列表的队列)

#### get_fission(self)
获取当前原子的 Fission 对象, 用于单原子调度展开

## Fission - 单原子调度控制器
### 属性
#### 状态属性
- exammode: 测试模式(默认)
- retronly: 仅回顾模式
#### 其他属性
- cursor
- atom
- current_puzzle
- orbital_schedule
- orbital_puzzles
- puzzles
### 初始化
接受 atom 对象和 phase 参数
### 方法
#### get_puzzles(self)