"""Configuration settings for the bioreactor system"""

class BioreactorConfig:
    # BCM Pin Mapping
    BCM_MAP = {
        7: 4, 11: 17, 12: 18, 13: 27, 15: 22, 16: 23, 18: 24, 22: 25,
        29: 5, 31: 6, 32: 12, 33: 13, 35: 19, 36: 16, 37: 26, 38: 20, 40: 21
    }
    
    # LED Configuration
    LED_PIN: int = 37
    LED_MODE: str = 'bcm'
    
    # ADC Configurations
    ADS1115_ADDRESS: int = 0x49
    ADS7830_REF_VOLTAGE: float = 4.2
    
    # BME280 Configurations
    BME280_ADDRESS: int = 0x76
    BME280_ATM_ADDRESS: int = 0x77
    BME_COUNT: int = 4
    
    # Sensor Arrays
    EXTERNAL_SENSOR_ORDER: list[int] = [2, 0, 3, 1]
    
    # I2C Multiplexer
    MUX_ADDRESS: int = 0x70
    
    # Logging Configuration
    LOG_LEVEL: str = 'INFO'
    LOG_FORMAT: str = '%(asctime)s - %(levelname)s - %(message)s'
