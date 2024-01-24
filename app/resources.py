from .extensions import api
ns = api.namespace("api")
# Route to user
# import app.controller.user  # noqa: E402

# Route to auth
import app.controller.auth  # noqa: E402

# Route to kapal
import app.controller.kapal  # noqa: E402

# Route to client
import app.controller.client # noqa: E402

# Route to Socket
import app.controller.mapping # noqa: E402

# Route to Socket
import app.controller.socket # noqa: E402





