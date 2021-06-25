import os
import logging
import click
from .delete_empty_log_streams import delete_empty_log_streams
from .delete_empty_log_groups import delete_empty_log_groups
from .set_log_retention import set_log_retention


@click.group()
@click.pass_context
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="do not change anything, just show what is going to happen",
)
@click.option("--region", help="aws region to connect to", required=False)
@click.option("--profile", help="aws profile to use to connect", required=False)
def main(ctx, dry_run, region, profile):
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "WARN"))
    ctx.obj = ctx.params


@main.command(name="set-log-retention")
@click.pass_context
@click.option("--days", type=int, required=False, default=30, help="retention period")
@click.option(
    "--overwrite", is_flag=True, default=False, help="existing retention periods"
)
@click.option(
    "--log-group-name-prefix",
    type=str,
    required=False,
    help="of selected log group only",
)
def set_log_retention_command(ctx, log_group_name_prefix, days, overwrite):
    set_log_retention(
        log_group_name_prefix,
        days,
        overwrite,
        ctx.obj["dry_run"],
        ctx.obj["region"],
        ctx.obj["profile"],
    )


@main.command(name="delete-empty-log-streams")
@click.pass_context
@click.option(
    "--log-group-name-prefix",
    type=str,
    required=False,
    help="of selected log group only",
)
@click.option(
    "--purge-non-empty",
    is_flag=True,
    default=False,
    help="purge non empty streams older than retention period too",
)
def delete_empty_log_streams_command(ctx, log_group_name_prefix, purge_non_empty):
    delete_empty_log_streams(
        log_group_name_prefix,
        purge_non_empty,
        ctx.obj["dry_run"],
        ctx.obj["region"],
        ctx.obj["profile"],
    )


@main.command(name="delete-empty-log-groups")
@click.pass_context
@click.option(
    "--log-group-name-prefix",
    type=str,
    required=False,
    help="of selected log group only",
)
def delete_empty_log_groups_command(ctx, log_group_name_prefix):
    delete_empty_log_groups(
        log_group_name_prefix,
        ctx.obj["dry_run"],
        ctx.obj["region"],
        ctx.obj["profile"],
    )


if __name__ == "__main__":
    main()
