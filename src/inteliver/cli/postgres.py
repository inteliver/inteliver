from pathlib import Path

import psycopg2
import typer
from alembic import command
from alembic.config import Config
from rich.prompt import Prompt

from inteliver.config import settings
from inteliver.config.utils import save_config_to_yaml

cli = typer.Typer()


def check_postgres_connectivity(dsn_sync: str) -> bool:
    """
    Checks PostgreSQL connectivity using the provided DSN.
    """
    try:
        conn = psycopg2.connect(dsn_sync)
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        conn.close()
        return True
    except psycopg2.OperationalError as e:
        typer.secho(f"PostgreSQL connection failed: {e}", fg=typer.colors.RED)
        typer.secho(
            "Please ensure that PostgreSQL is up and running on the specified host and port, "
            "and that the username and password are correct.",
            fg=typer.colors.YELLOW,
        )
        return False


def prompt_postgres_fields(
    default_postgres_user: str,
    default_postgres_password: str,
    default_postgres_host: str,
    default_postgres_port: int,
    default_postgres_db: str,
):
    postgres_user = Prompt.ask(
        "Enter the PostgreSQL username", default=default_postgres_user
    )
    postgres_password = Prompt.ask(
        "Enter the PostgreSQL password",
        password=True,
        default=default_postgres_password,
    )
    postgres_host = Prompt.ask(
        "Enter the PostgreSQL host", default=default_postgres_host
    )
    postgres_port = Prompt.ask(
        "Enter the PostgreSQL port", default=str(default_postgres_port)
    )
    postgres_db = Prompt.ask(
        "Enter the PostgreSQL database name", default=default_postgres_db
    )
    return postgres_user, postgres_password, postgres_host, postgres_port, postgres_db


def setup_postgres(
    non_interactive: bool,
    postgres_user: str,
    postgres_password: str,
    postgres_host: str,
    postgres_port: int,
    postgres_db: str,
) -> tuple[bool, dict]:
    """
    Initialize postgres setup and check connectivity.
    """
    # Non-interactive mode: Use settings if not provided through command options
    if non_interactive:
        dsn_sync = f"dbname={postgres_db} user={postgres_user} password={postgres_password} host={postgres_host} port={postgres_port}"
        # dsn_async = f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
        if check_postgres_connectivity(dsn_sync):
            # Save the DSN in settings
            settings.postgres_user = postgres_user
            settings.postgres_password = postgres_password
            settings.postgres_host = postgres_host
            settings.postgres_port = int(postgres_port)
            settings.postgres_db = postgres_db

            config = {
                "postgres_user": settings.postgres_user,
                "postgres_password": settings.postgres_password,
                "postgres_host": settings.postgres_host,
                "postgres_port": settings.postgres_port,
                "postgres_db": settings.postgres_db,
            }
            return True, config
        else:
            typer.secho(
                "Non-interactive mode: Exiting due to failed connection.",
                fg=typer.colors.RED,
            )
        return False, {}

    # Interactive mode: Prompt user for each part of the DSN
    else:
        use_default = Prompt.ask(
            f"Do you want to use the default PostgreSQL DSN?\n"
            f"(user={postgres_user}, password={postgres_password}, "
            f"host={postgres_host}, port={postgres_port}, db={postgres_db})",
            choices=["yes", "no"],
            default="yes",
        )

        if use_default == "no":
            (
                postgres_user,
                postgres_password,
                postgres_host,
                postgres_port,
                postgres_db,
            ) = prompt_postgres_fields(
                default_postgres_user=postgres_user,
                default_postgres_password=postgres_password,
                default_postgres_host=postgres_host,
                default_postgres_port=postgres_port,
                default_postgres_db=postgres_db,
            )

        dsn_sync = f"dbname={postgres_db} user={postgres_user} password={postgres_password} host={postgres_host} port={postgres_port}"
        # dsn_async = f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

    max_attempt_num = 3
    # Check PostgreSQL connectivity
    for attempt in range(max_attempt_num):
        typer.secho(
            "Attempting to connect to the postgres database with provided settings.",
            fg=typer.colors.CYAN,
        )
        typer.secho(
            f"Attempt {attempt + 1} out of {max_attempt_num}...", fg=typer.colors.CYAN
        )
        if check_postgres_connectivity(dsn_sync):
            # Save the DSN in settings
            settings.postgres_user = postgres_user
            settings.postgres_password = postgres_password
            settings.postgres_host = postgres_host
            settings.postgres_port = int(postgres_port)
            settings.postgres_db = postgres_db

            config = {
                "postgres_user": settings.postgres_user,
                "postgres_password": settings.postgres_password,
                "postgres_host": settings.postgres_host,
                "postgres_port": settings.postgres_port,
                "postgres_db": settings.postgres_db,
            }
            return True, config
        else:
            # Reprompt user for connection details in case of failure
            (
                postgres_user,
                postgres_password,
                postgres_host,
                postgres_port,
                postgres_db,
            ) = prompt_postgres_fields(
                default_postgres_user=postgres_user,
                default_postgres_password=postgres_password,
                default_postgres_host=postgres_host,
                default_postgres_port=postgres_port,
                default_postgres_db=postgres_db,
            )

            dsn_sync = f"dbname={postgres_db} user={postgres_user} password={postgres_password} host={postgres_host} port={postgres_port}"
            # dsn_async = f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

    return False, {}


@cli.command()
def setup(
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        help="Init Inteliver using default config settings in a non-interactive way.",
    ),
    postgres_user: str = typer.Option(
        settings.postgres_user, "--postgres-user", help="Postgres connection user."
    ),
    postgres_password: str = typer.Option(
        settings.postgres_password,
        "--postgres-password",
        help="Postgres connection password.",
    ),
    postgres_host: str = typer.Option(
        settings.postgres_host, "--postgres-host", help="Postgres connection host."
    ),
    postgres_port: int = typer.Option(
        settings.postgres_port, "--postgres-port", help="Postgres connection port."
    ),
    postgres_db: str = typer.Option(
        settings.postgres_db, "--postgres-db", help="Postgres database name."
    ),
):
    """
    Initialize inteliver database setup.
    """
    # Initialize an empty config data dictionary
    config_data = {}

    # Step 1: PostgreSQL Setup
    typer.secho("Setting up PostgreSQL...", fg=typer.colors.BLUE)
    postgres_success, postgres_config = setup_postgres(
        non_interactive=non_interactive,
        postgres_user=postgres_user,
        postgres_password=postgres_password,
        postgres_host=postgres_host,
        postgres_port=postgres_port,
        postgres_db=postgres_db,
    )
    if not postgres_success:
        typer.secho("PostgreSQL setup failed. Exiting.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    config_data.update(postgres_config)
    typer.secho("Updating config file...", fg=typer.colors.CYAN)
    # Save configuration to YAML
    save_config_to_yaml(config_data)
    typer.secho("PostgreSQL setup completed.", fg=typer.colors.GREEN)


def migrate_postgres():
    """
    Migrate the Inteliver PostgreSQL database to the latest version using Alembic.

    This function executes the Alembic command to apply any new migrations to the database.
    """
    # # Assume that the alembic.ini file is located at the root of your project
    inteliver_package_root = Path(__file__).parent.parent
    alembic_ini_path = inteliver_package_root / "alembic.ini"
    alembic_migerations_path = inteliver_package_root / "alembic"

    # Check if alembic.ini exists
    if not alembic_ini_path.exists():
        typer.secho(
            f"Error: '{alembic_ini_path}' not found. Ensure the alembic.ini file is present.",
            fg=typer.colors.RED,
        )
        raise FileNotFoundError(f"Missing alembic.ini file at {alembic_ini_path}")

    # Check if the alembic directory exists
    if not alembic_migerations_path.exists():
        typer.secho(
            f"Error: '{alembic_migerations_path}' directory not found. Ensure the alembic folder is present.",
            fg=typer.colors.RED,
        )
        raise FileNotFoundError(
            f"Missing alembic directory at {alembic_migerations_path}"
        )

    try:
        # Load the alembic configuration
        alembic_cfg = Config(alembic_ini_path)

        # Override the script_location to point to the correct alembic folder
        alembic_cfg.set_main_option("script_location", str(alembic_migerations_path))

        # Run the migration
        command.upgrade(alembic_cfg, "head")

    except Exception as e:
        # Handle any exceptions during migration
        typer.secho(f"Migration failed: {e}", fg=typer.colors.RED)
        raise


@cli.command()
def migrate():
    """
    Command to migrate the Inteliver PostgreSQL database to the latest version.
    """
    migrate_postgres()
