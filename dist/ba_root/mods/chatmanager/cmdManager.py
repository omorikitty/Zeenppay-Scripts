import time
from .handle import get_uniqueid, is_admin, sendmsg


class CommandManager:
    """Esta clase esta hecha para proporcionar un mayor control sobre nuestros comandos."""

    def __init__(
        self,
        max_commands_per_minute: int = 5,
        cooldown_duration: int = 10,
        admin_bypass_threshold: int = 5,
    ):
        """Inicializa el CommandManager.

        Args:
            max_commands_per_minute (int): Maximos comandos por minutos. Defaults to 5.
            cooldown_duration (int): duracion de comandos por minutos. Defaults to 5.
            admin_bypass_threshold (int): Maximos comandos por admins. Defaults to 3.
        """
        #self.command_count = {}
        self.max_commands_per_minute = max_commands_per_minute
        self.command_cooldowns = {}
        self.cooldown_duration = cooldown_duration
        self.admin_bypass_threshold = admin_bypass_threshold

    def process_command(self, command, client_id, account_id=None):
        """Procesa un comando y aplica periodos de espera si es necesario.

        Args:
            command (str): El comando que se va a procesar.
            client_id (int): El ID del cliente que inicia el comando.
            account_id (str, opcional): El ID de la cuenta del cliente. Default to None.

        Returns:
            bool: True si se permite el comando, False en caso contrario.
        """

        current_time = time.time()

        # Verifica si el comando esta en un periodo de espera
        if command not in self.command_cooldowns:
            self.command_cooldowns[command] = {}


        if (
            client_id in self.command_cooldowns[command]
            and current_time - self.command_cooldowns[command][client_id]["last"]
            < self.cooldown_duration
        ):
            remaining = int(
                self.cooldown_duration
                - (current_time - self.command_cooldowns[command][client_id]["last"])
            )
            sendmsg(
                f"Demasiadas Solicitudes Espera {remaining}s.",
                client_id,
                color=(0.8, 0.7, 0.5),
            )
            # reinicia el contador para que pueda seguir usando el comando.
            self.command_cooldowns[command][client_id]["count"] = 1
            return False

        # Actualiza el recuento de comandos para el usuario
        if client_id in self.command_cooldowns[command]:
            self.command_cooldowns[command][client_id]["count"] += 1
        else:
            self.command_cooldowns[command][client_id] = {"count": 1, "last": 0}

        # Verifica si el usuario ha superado el limite maximo de comandos por minuto
        if self.command_cooldowns[command][client_id]["count"] > self.max_commands_per_minute:
            # Si el usuario supera el umbral, aplica un periodo de espera mas largo
            self.command_cooldowns[command][client_id]["last"] = (
                current_time + self.cooldown_duration
            )
            return False

        # Bypass para administradores
        if account_id is not None and is_admin(account_id):
            if self.command_cooldowns[command][client_id]["count"] > self.admin_bypass_threshold:
                # Si un administrador supera el umbral, reduce el periodo de espera
                self.command_cooldowns[command][client_id]["last"] = (
                    current_time + self.cooldown_duration / 2
                )

            return True

        return True
