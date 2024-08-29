import typer
from minio import Minio, S3Error
from rich.prompt import Prompt

from inteliver.config import settings
from inteliver.config.utils import save_config_to_yaml

cli = typer.Typer()


# Check MinIO connectivity
def check_minio_connectivity(
    host: str, root_user: str, root_password: str, minio_secure: bool
) -> bool:
    try:
        client = Minio(
            endpoint=host,
            access_key=root_user,
            secret_key=root_password,
            secure=minio_secure,
        )
        # Perform a simple action to verify connectivity
        client.list_buckets()
        return True
    except S3Error as e:
        typer.secho(f"MinIO connection failed: {e}", fg=typer.colors.RED)
        return False
    except Exception as e:
        typer.secho(f"MinIO connection failed: {e}", fg=typer.colors.RED)
        return False


def prompt_minio_fields(
    default_minio_host: str,
    default_minio_root_user: str,
    default_minio_root_password: str,
):
    minio_host = Prompt.ask(
        "Enter the MinIO host and port (Example: minio:9000)",
        default=default_minio_host,
    )
    minio_root_user = Prompt.ask(
        "Enter the MinIO root user", default=default_minio_root_user
    )
    minio_root_password = Prompt.ask(
        "Enter the MinIO root password",
        default=default_minio_root_password,
        password=True,
    )
    minio_secure_prompt = Prompt.ask(
        "Use HTTPS for MinIO? (yes/no)",
        choices=["yes", "no"],
        default="no",
    )
    minio_secure = minio_secure_prompt == "yes"
    return minio_host, minio_root_user, minio_root_password, minio_secure


def setup_minio(
    non_interactive: bool,
    minio_host: str,
    minio_root_user: str,
    minio_root_password: str,
    minio_secure: bool,
) -> tuple[bool, dict]:
    """
    Setup MinIO server and check connectivity.
    """

    # Non-interactive mode: Use settings if not provided through command options
    if non_interactive:
        typer.secho(
            f"Using default MinIO settings: host={minio_host} user={minio_root_user} password={minio_root_password}",
            fg=typer.colors.CYAN,
        )
        if check_minio_connectivity(
            minio_host, minio_root_user, minio_root_password, minio_secure
        ):
            # Save the MinIO settings
            settings.minio_host = minio_host
            settings.minio_root_user = minio_root_user
            settings.minio_root_password = minio_root_password
            settings.minio_secure = minio_secure

            config = {
                "minio_host": settings.minio_host,
                "minio_root_user": settings.minio_root_user,
                "minio_root_password": settings.minio_root_password,
                "minio_secure": settings.minio_secure,
            }
            return True, config
        else:
            typer.secho(
                "Non-interactive mode: Exiting due to failed connection.",
                fg=typer.colors.RED,
            )
        return False, {}

    else:
        use_default = Prompt.ask(
            f"Do you want to use the default MinIO settings?\n"
            f"(host={minio_host}, user={minio_root_user}, password={minio_root_password}, secure={minio_secure})",
            choices=["yes", "no"],
            default="yes",
        )

        if use_default == "no":
            minio_host, minio_root_user, minio_root_password, minio_secure = (
                prompt_minio_fields(
                    default_minio_host=minio_host,
                    default_minio_root_user=minio_root_user,
                    default_minio_root_password=minio_root_password,
                )
            )

    max_attempt_num = 3
    # Check MinIO connectivity
    for attempt in range(max_attempt_num):
        typer.secho(
            "Attempting to connect to the MinIO database with provided settings.",
            fg=typer.colors.CYAN,
        )
        typer.secho(
            f"Attempt {attempt + 1} out of {max_attempt_num}...", fg=typer.colors.CYAN
        )
        if check_minio_connectivity(
            host=minio_host,
            root_user=minio_root_user,
            root_password=minio_root_password,
            minio_secure=minio_secure,
        ):
            # Save the MinIO settings
            settings.minio_host = minio_host
            settings.minio_root_user = minio_root_user
            settings.minio_root_password = minio_root_password
            settings.minio_secure = minio_secure

            config = {
                "minio_host": settings.minio_host,
                "minio_root_user": settings.minio_root_user,
                "minio_root_password": settings.minio_root_password,
                "minio_secure": settings.minio_secure,
            }
            return True, config
        else:
            # Reprompt user for connection details in case of failure
            minio_host, minio_root_user, minio_root_password, minio_secure = (
                prompt_minio_fields(
                    default_minio_host=minio_host,
                    default_minio_root_user=minio_root_user,
                    default_minio_root_password=minio_root_password,
                )
            )

    # Save the MinIO settings
    return False, {}


@cli.command()
def setup(
    non_interactive: bool = typer.Option(
        False,
        "--none-interactive",
        help="Setup MinIO using default config settings in a non-interactive way.",
    ),
    minio_host: str = typer.Option(
        settings.minio_host, "--minio-host", help="MinIO server host and port."
    ),
    minio_root_user: str = typer.Option(
        settings.minio_root_user, "--minio-root-user", help="MinIO root user."
    ),
    minio_root_password: str = typer.Option(
        settings.minio_root_password,
        "--minio-root-password",
        help="MinIO root password.",
    ),
    minio_secure: bool = typer.Option(
        settings.minio_secure, "--minio-secure", help="Use HTTPS for MinIO."
    ),
):
    """
    Initialize inteliver minio setup.
    """
    # Initialize an empty config data dictionary
    config_data = {}
    typer.secho("Setting up MinIO...", fg=typer.colors.BLUE)

    minio_success, minio_config = setup_minio(
        non_interactive=non_interactive,
        minio_host=minio_host,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        minio_secure=minio_secure,
    )
    if not minio_success:
        typer.secho("MinIO setup failed. Exiting.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    config_data.update(minio_config)
    typer.secho("Updating config file...", fg=typer.colors.CYAN)
    # Save configuration to YAML
    save_config_to_yaml(config_data)
    typer.secho("MinIO setup completed.", fg=typer.colors.GREEN)
