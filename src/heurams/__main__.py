import platform

import click
from heurams.services.version import ver, stage, codename, codename_cn


@click.group(
    invoke_without_command=True,
    help=(
        f"HeurAMS {ver} - 启发式辅助记忆调度器"
    ),
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option(
    ver, "-v", "--version",
    prog_name="HeurAMS",
    message=f"%(prog)s %(version)s {stage} ({codename}/{codename_cn}), {platform.system()}",
)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(cli.get_help(ctx))
        ctx.exit(0)


@cli.command()
def tui():
    """启动内置基本用户界面 (TUI)"""
    import heurams.interface.__main__ as tui_module

    tui_module.main()


def _print_version():
    click.echo(
        f"HeurAMS {ver} ({codename}/{codename_cn}), 阶段: {stage}"
    )


@cli.command()
def version():
    """输出版本信息"""
    _print_version()


@cli.command(name="ver", hidden=True)
def ver_cmd():
    """输出版本信息"""
    _print_version()


@cli.command(name="help")
@click.pass_context
def help_cmd(ctx):
    """显示此帮助信息"""
    click.echo(cli.get_help(ctx.parent))


def main():
    cli()


if __name__ == "__main__":
    main()
