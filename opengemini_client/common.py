class Address:
    """
    Address configuration for providing service
    """

    def __init__(self, host: str, port: int):
        """
        :param host: service ip or domain.
        :param port: exposed service port
        """
        self.host = host
        self.port = port


class AuthType:
    """
    AuthType represents the type of identity authentication
    """
    AUTH_TYPE_PASSWORD = 0
    AUTH_TYPE_TOKE = 1


class AuthConfig:
    """
    AuthConfig represents the configuration for authentication
    """

    def __init__(self, auth_type: AuthType, username: str, password: str, token: str) -> None:
        """

        :param auth_type: AuthType represents the type of identity authentication
        :param username: provided username when  AuthTypePassword is used
        :param password:  provided password when  AuthTypePassword is used
        :param token: provided token when  AuthTypeToken is used
        """
        self.auth_type = auth_type
        self.username = username
        self.password = password
        self.token = token


class BatchConfig:
    """
    BatchConfig represents the configuration for batch processing
    """

    def __init__(self, batch_interval: int, batch_size: int):
        """
        :param batch_interval: batch time interval that triggers batch processing.(unit: ms)
        :param batch_size: batch size that triggers batch processing.
        """
        self.batch_interval = batch_interval
        self.batch_size = batch_size


class RpCconfig:
    """
    RpCconfig represents the configuration for retention policy
    """

    def __init__(self, name: str, duration: str, shard_group_duration: str, index_duration: str):
        """
        :param name: retention policy name
        :param duration: indicates how long the data will be retained
        :param shard_group_duration: determines the time range for sharding groups
        :param index_duration: determines the time range of the index group
        """
        self.name = name
        self.duration = duration
        self.shard_group_duration = shard_group_duration
        self.index_duration = index_duration


class Config:
    """
     configuration of the service URL for the openGemini service
    """

    def __init__(self, address: list[Address], auth_config: AuthConfig, batch_config: BatchConfig,
                 timeout, connection_timeout, gzip_enabled: bool, tls_enabled: bool,
                 tls_config: bool):
        """
        :param address: This parameter is required
        :param auth_config: AuthConfig configration information for authentication
        :param batch_config: BatchConfig configration information for batch processing
        :param timeout: default 30s
        :param connection_timeout:  ConnectionTimeout default 10s
        :param gzip_enabled: determines whether to use gzip compression for data transmission
        :param tls_enabled: determines whether to use TLS encryption for data transmission
        :param tls_config: configration information for tls authentication
        """
        self.address = address
        self.auth_config = auth_config
        self.batch_config = batch_config
        self.timeout = timeout
        self.connection_timeout = connection_timeout
        self.gzip_enabled = gzip_enabled
        self.tls_enabled = tls_enabled
        self.tls_config = tls_config
