import reflex as rx
from pydantic import BaseModel, Field
import json
import base64
import logging
from typing import Optional


class Env(BaseModel):
    name: str = ""
    host: str = "localhost"
    port: int = 5432
    database: str = ""
    username: str = ""
    password: str = ""
    ssh_host: Optional[str] = None
    ssh_port: int = 22
    ssh_user: Optional[str] = None
    ssh_key: Optional[str] = None


class CredentialsState(rx.State):
    environments_json: str = rx.LocalStorage(name="db_environments_v2")
    active_environment: str = rx.LocalStorage(name="active_db_environment_v2")
    environments: list[Env] = []
    current_env: Env = Env()
    show_modal: bool = False

    @rx.event
    def load_credentials(self):
        """Load environments from local storage."""
        if self.environments_json:
            try:
                decoded_json = base64.b64decode(self.environments_json).decode()
                self.environments = [Env(**e) for e in json.loads(decoded_json)]
            except Exception as e:
                logging.exception(f"Failed to load credentials: {e}")
                self.environments_json = ""
        if not self.active_environment and self.environments:
            self.active_environment = self.environments[0].name

    @rx.event
    def save_current_environment(self, form_data: dict):
        """Save the current environment details from the form."""
        name = form_data.get("name")
        if not name:
            yield rx.toast.error("Environment name cannot be empty.")
            return
        try:
            new_env = Env(
                name=name,
                host=form_data.get("host", "localhost"),
                port=int(form_data.get("port", 5432)),
                database=form_data.get("database", ""),
                username=form_data.get("username", ""),
                password=form_data.get("password", ""),
                ssh_host=form_data.get("ssh_host"),
                ssh_port=int(form_data.get("ssh_port", 22)),
                ssh_user=form_data.get("ssh_user"),
                ssh_key=form_data.get("ssh_key"),
            )
        except (ValueError, TypeError) as e:
            logging.exception(f"Error parsing form data: {e}")
            yield rx.toast.error("Invalid port number.")
            return
        idx = next(
            (i for i, env in enumerate(self.environments) if env.name == new_env.name),
            -1,
        )
        if idx != -1:
            self.environments[idx] = new_env
        else:
            self.environments.append(new_env)
        self._save_to_local_storage()
        if not self.active_environment:
            self.active_environment = new_env.name
        yield self._reload_schema()
        yield rx.toast.success(f"Saved environment: {new_env.name}")
        self.current_env = Env()

    def _save_to_local_storage(self):
        env_list = [env.model_dump() for env in self.environments]
        encoded_json = base64.b64encode(json.dumps(env_list).encode()).decode()
        self.environments_json = encoded_json

    @rx.event
    def set_active_environment(self, env_name: str):
        """Set the active environment and reload schema."""
        self.active_environment = env_name
        yield from self._reload_schema()

    def _reload_schema(self):
        from .dashboard_state import DashboardState
        from .db_state import DatabaseState

        yield DashboardState.set_selected_table("")
        return DatabaseState.fetch_schema

    @rx.event
    def delete_environment(self, env_name: str):
        """Delete an environment."""
        self.environments = [env for env in self.environments if env.name != env_name]
        if self.active_environment == env_name:
            self.active_environment = (
                self.environments[0].name if self.environments else ""
            )
        self._save_to_local_storage()
        yield from self._reload_schema()

    @rx.event
    def edit_environment(self, env_name: str):
        """Load an environment into the form for editing."""
        env = next((env for env in self.environments if env.name == env_name), None)
        if env:
            self.current_env = env.copy()
            yield CredentialsState.toggle_modal(True)

    @rx.event
    def set_current_env_field(self, field: str, value: str):
        """Update a field in the current_env being edited."""
        try:
            if field == "port":
                setattr(self.current_env, field, int(value))
            else:
                setattr(self.current_env, field, value)
        except (ValueError, TypeError) as e:
            logging.exception(f"Error setting env field: {e}")

    @rx.event
    def toggle_modal(self, show: bool):
        """Toggle the credentials modal visibility."""
        self.show_modal = show
        if not show:
            self.current_env = Env()

    @rx.var
    def get_active_env(self) -> Env | None:
        return next(
            (env for env in self.environments if env.name == self.active_environment),
            None,
        )