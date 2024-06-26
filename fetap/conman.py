from typing import TYPE_CHECKING

import logging

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    import fetap.fake_gpio as _gpio
else:
    try:
        import RPi.GPIO as _gpio
    except ImportError:
        log.warning("Using fake GPIO")
        import fetap.fake_gpio as _gpio

gpio = _gpio
