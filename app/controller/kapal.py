from app.extensions import db, generate_random_string
from flask_restx import Resource, reqparse
from app.api_model.kapal import (
    get_kapal_model,
    insert_client_parser,
)
from app.model.kapal import Kapal
from app.resources import ns
import datetime

# Pagination parameters
pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument("page", type=int, help="Page number", default=1)
pagination_parser.add_argument("per_page", type=int, help="Items per page", default=10)


@ns.route("/kapal")
class KapalList(Resource):
    @ns.marshal_list_with(get_kapal_model)
    @ns.expect(pagination_parser)
    def get(self):
        args = pagination_parser.parse_args()
        page = args["page"]
        per_page = args["per_page"]
        offset = (page - 1) * per_page

        total_count = Kapal.query.count()

        kapal = Kapal.query.offset(offset).limit(per_page).all()

        return {
            "message": "Data Kapal Ditemukan",
            "status": 200,
            "page": page,
            "perpage": per_page,
            "total": total_count,
            "data": kapal,
        }, 200

    @ns.expect(insert_client_parser)
    def post(self):
        try:
            args = insert_client_parser.parse_args()
            call_sign = args["call_sign"]
            id_client = args["id_client"]
            flag = args["flag"]
            kelas = args["kelas"]
            builder = args["builder"]
            year_built = args["year_built"]
            size = args["size"]
            status = args["status"]
            uploaded_file = args["xml_file"]

            # Do something with the uploaded file, for example, save it
            allowed_extensions = {"xml", "png"}
            if (
                "." in uploaded_file.filename
                and uploaded_file.filename.rsplit(".", 1)[1].lower()
                in allowed_extensions
            ):
                # File Name
                current_datetime = datetime.datetime.now()
                str_datetime = current_datetime.strftime("%Y_%m_%d_%H_%M_%S")
                file_path = "assets/kapal/"
                file_name = (
                    f"{str_datetime}_{call_sign}."
                    + uploaded_file.filename.rsplit(".", 1)[1].lower()
                )

                # Upload Kapal
                kapal = Kapal(
                    call_sign=call_sign,
                    id_client=id_client,
                    flag=flag,
                    kelas=kelas,
                    builder=builder,
                    year_built=year_built,
                    size=size,
                    status=status,
                    xml_file=file_name,
                )

                db.session.add(kapal)

                # File Uploaded
                uploaded_file.save(file_path + file_name)

                # db.session.commit()
                return {"message": "Kapal uploaded successfully"}
            else:
                return {
                    "message": "Invalid file extension. Allowed extensions: .xml"
                }, 400
        except AssertionError as exception_message:
            db.session.rollback()
            return {"message": "{}.".format(str(exception_message))}, 400
        except TypeError as e:
            db.session.rollback()
            return {"message": str(e)}, 404
        except Exception as e:
            db.session.rollback()
            return {"message": str(e)}, 500
