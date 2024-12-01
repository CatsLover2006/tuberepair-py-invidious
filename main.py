# Version v0.0.3 (beta 1)
from flask import Flask
from flask_compress import Compress
import config

# seperated apis
from api.static import static
from api.playlist import playlist
from api.video import video
from api.channel import channel
from modules import logs

# init
# Load version text
logs.version(config.VERSION)
app = Flask(__name__)

# register seperate paths
app.register_blueprint(static)
app.register_blueprint(playlist)
app.register_blueprint(video)
app.register_blueprint(channel)

# use compression to load faster
compress = Compress(app)

# config
if __name__ == "__main__":
    app.run(port=config.PORT, host="0.0.0.0", debug=config.DEBUG)
