from .extensions import api
ns = api.namespace("api")


# Route to user
import app.controller.user  # noqa: E402

# Route to user
import app.controller.kapal  # noqa: E402

# Route to client
import app.controller.client # noqa: E402





