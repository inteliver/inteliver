import typer
from rich.prompt import Prompt
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from inteliver.auth.utils import get_password_hash
from inteliver.config import settings
from inteliver.users.models import User
from inteliver.users.schemas import UserCreate

cli = typer.Typer()


def get_session() -> Session:
    """
    Create and return a SQLAlchemy session for PostgreSQL.
    """
    dsn = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}/{settings.postgres_db}"
    engine = create_engine(dsn)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    return session


def insert_admin(db_session: Session, user_data: UserCreate) -> bool:
    """
    Insert a new user with an admin role in the database.
    """
    try:
        # Check if user already exists
        user_exists = (
            db_session.query(User)
            .filter_by(email_username=user_data.email_username)
            .first()
        )

        if user_exists:
            typer.secho(
                f"User with email {user_data.email_username} already exists.",
                fg=typer.colors.YELLOW,
            )
            return True

        # Create a new user
        new_user = User(
            name=user_data.name,
            cloudname=user_data.cloudname,
            email_username=user_data.email_username,
            password=user_data.password,  # Password should be hashed in real implementations
            role="admin",
        )
        new_user.password = get_password_hash(user_data.password)
        db_session.add(new_user)
        db_session.commit()
        typer.secho("Admin user created successfully!", fg=typer.colors.CYAN)
        return True
    except IntegrityError as e:
        db_session.rollback()
        typer.secho(f"Error creating admin user: {e}", fg=typer.colors.RED)
        return False


def create_admin(
    non_interactive: bool,
    name: str,
    email_username: str,
    cloudname: str,
    password: str,
):
    if not non_interactive:
        create_admin = Prompt.ask(
            "Do you want to create an admin user?", choices=["yes", "no"], default="yes"
        )
        if create_admin == "yes":
            name = Prompt.ask("Enter the admin's name", default=name)
            email_username = Prompt.ask(
                "Enter the admin's email/username", default=email_username
            )
            cloudname = Prompt.ask("Enter the admin's cloudname", default=cloudname)
            password = Prompt.ask(
                "Enter the admin's password", password=True, default=password
            )

            user_data = UserCreate(
                name=name,
                email_username=email_username,
                cloudname=cloudname,
                password=password,
            )

            # Insert admin user into postgres db
            db_session = get_session()
            if not insert_admin(db_session, user_data):
                typer.secho(
                    "Failed to create admin user. Exiting.", fg=typer.colors.RED
                )
                return
            db_session.close()
        else:
            typer.secho("Skipping admin user creation.", fg=typer.colors.YELLOW)

    # Non-interactive mode: Use default settings
    else:
        typer.secho(
            "Non-interactive mode: Skipping admin user creation.",
            fg=typer.colors.YELLOW,
        )


@cli.command()
def create(
    non_interactive: bool = typer.Option(
        False,
        "--none-interactive",
        help="Setup a default admin user using default config settings in a non-interactive way.",
    ),
    name: str = typer.Option("admin", "--admin-name", help="Admin user name."),
    email_username: str = typer.Option(
        "you@inteliver.com", "--admin-email-username", help="Admin user email."
    ),
    cloudname: str = typer.Option(
        "inteliver",
        "--admin-cloudname",
        help="Admin user cloudname.",
    ),
    password: str = typer.Option(
        "password", "--admin-password", help="Admin user password."
    ),
):
    """
    Create inteliver admin user.
    """
    create_admin(
        non_interactive,
        name,
        email_username,
        cloudname,
        password,
    )
