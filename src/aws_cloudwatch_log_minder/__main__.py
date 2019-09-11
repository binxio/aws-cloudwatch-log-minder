import os
import click
from .delete_empty_log_streams import delete_empty_log_streams
from .set_log_retention import set_log_retention

@click.group()
@click.pass_context
@click.option('--dry-run', is_flag=True, default=False,
              help='do not change anything, just show what is going to happen')
def main(ctx, dry_run):
    ctx.obj = ctx.params

@main.command(name='set-log-retention')
@click.pass_context
@click.option('--days', type=int, required=False, default=30)
def set_log_retention_command(ctx, days):
    set_log_retention(days, ctx.obj['dry_run'])

@main.command(name='delete-empty-log-streams')
@click.pass_context
def delete_empty_log_streams_command(ctx):
    delete_empty_log_streams(ctx.obj['dry_run'])

if __name__ == '__main__':
    main()
