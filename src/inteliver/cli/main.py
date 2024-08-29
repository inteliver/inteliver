import typer

from inteliver.cli.minio import cli as subcommand_minio
from inteliver.cli.minio import setup_minio
from inteliver.cli.postgres import cli as subcommand_postgres
from inteliver.cli.postgres import migrate_postgres, setup_postgres
from inteliver.cli.user import cli as subcommand_adminuser
from inteliver.cli.user import create_admin
from inteliver.cli.utils import print_inteliver_logo
from inteliver.config import settings
from inteliver.config.utils import save_config_to_yaml
from inteliver.version import __version__

cli = typer.Typer()


cli.add_typer(
    subcommand_postgres,
    name="db",
    help="All subcommands related to PostgreSQL database",
)

cli.add_typer(
    subcommand_minio,
    name="storage",
    help="All subcommands related to MinIO storage",
)

cli.add_typer(
    subcommand_adminuser,
    name="adminuser",
    help="All subcommands related to admin user",
)


@cli.command()
def run(host: str = settings.app_api_host, port: int = settings.app_api_port):
    """
    Run inteliver service.
    """
    print_inteliver_logo()

    from inteliver.main import run_service

    run_service(host, port)


@cli.command()
def init(
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        help="Init Inteliver using default config settings in a non-interactive way.",
    ),
    # environment: str = typer.Option(
    #     "development",
    #     "--environment",
    #     help="The environment for which to configure Inteliver (e.g., development, production).",
    # ),
):
    """
    Initialize Inteliver setup by sequentially running necessary subcommands.
    """
    # Initialize an empty config data dictionary
    config_data = {}

    # Step 1: PostgreSQL Setup
    typer.secho("Setting up PostgreSQL...", fg=typer.colors.BLUE)
    postgres_success, postgres_config = setup_postgres(
        non_interactive=non_interactive,
        postgres_user=settings.postgres_user,
        postgres_password=settings.postgres_password,
        postgres_host=settings.postgres_host,
        postgres_port=settings.postgres_port,
        postgres_db=settings.postgres_db,
    )
    if not postgres_success:
        typer.secho("PostgreSQL setup failed. Exiting.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    config_data.update(postgres_config)
    typer.secho("PostgreSQL setup completed.", fg=typer.colors.GREEN)

    # Step 2: Migrate Database
    typer.secho("Migrating the Inteliver database...", fg=typer.colors.BLUE)
    migrate_postgres()
    typer.secho("Database migration completed.", fg=typer.colors.GREEN)

    # Step 3: Minio Setup
    typer.secho("Setting up MinIO...", fg=typer.colors.BLUE)
    minio_success, minio_config = setup_minio(
        non_interactive=non_interactive,
        minio_host=settings.minio_host,
        minio_root_user=settings.minio_root_user,
        minio_root_password=settings.minio_root_password,
        minio_secure=settings.minio_secure,
    )

    if not minio_success:
        typer.secho("MinIO setup failed. Exiting.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    config_data.update(minio_config)
    typer.secho("MinIO setup completed.", fg=typer.colors.GREEN)

    # Step 4: Create Admin User
    typer.secho("Setting up admin user...", fg=typer.colors.BLUE)
    create_admin(
        non_interactive=non_interactive,
        name="admin",
        email_username="you@inteliver.com",
        cloudname="inteliver",
        password="password",
    )
    typer.secho("Admin user setup completed.", fg=typer.colors.GREEN)

    # Save configuration to YAML
    save_config_to_yaml(config_data)

    # Step 5: Upload Seed Images (if desired)

    settings.log_settings()

    typer.secho(
        "Inteliver initialization completed successfully!", fg=typer.colors.BRIGHT_GREEN
    )


@cli.command()
def version():
    """
    Output the current version of the inteliver.
    """
    print(f"🚀 {__version__}")


if __name__ == "__main__":
    cli()
