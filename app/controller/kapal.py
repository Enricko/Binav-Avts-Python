import os
from app.extensions import api_handle_exception, db, generate_random_string
from flask_restx import Resource, reqparse
from sqlalchemy.exc import IntegrityError
from app.api_model.kapal import (
    get_kapal_model,
    insert_kapal_parser,
    update_kapal_parser,
)
from app.model.kapal import Kapal
from app.resources import ns
import datetime

# Uploaded file path
file_path = "app/assets/kapal/"


# Pagination parameters
pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument("page", type=int, help="Page number", default=1)
pagination_parser.add_argument("per_page", type=int, help="Items per page", default=10)


@ns.route("/kapal")
class KapalList(Resource):
    @ns.marshal_list_with(get_kapal_model)
    @ns.expect(pagination_parser)
    @api_handle_exception
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

    @ns.expect(insert_kapal_parser)
    @api_handle_exception
    def post(self):
        args = insert_kapal_parser.parse_args()
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
        allowed_extensions = {"xml"}
        if uploaded_file is not None:
            if(
                "." in uploaded_file.filename
                and uploaded_file.filename.rsplit(".", 1)[1].lower()
                in allowed_extensions
            ):
                # File Name
                current_datetime = datetime.datetime.now()
                str_datetime = current_datetime.strftime("%Y_%m_%d_%H_%M_%S")
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

                db.session.commit()

                # File Uploaded
                uploaded_file.save(file_path + file_name)
                
                return {"message": "Kapal uploaded successfully."},201
            else:
                return {
                    "message": "Invalid file extension. Allowed extensions: .xml"
                }, 400
        else:
            return {
                "message": "xml_file field is required."
            }, 400
            
@ns.route("/kapal/<string:call_sign>")
class KapalData(Resource):
    @ns.marshal_list_with(get_kapal_model)
    @api_handle_exception
    def get(self,call_sign):
        kapal = Kapal.query.get(call_sign)

        return {
            "message": "Data Kapal Ditemukan",
            "status": 200,
            "page": 1,
            "perpage": 1,
            "total": 1,
            "data": kapal,
        }, 200
        
    @ns.expect(update_kapal_parser)
    @api_handle_exception
    def put(self,call_sign):
        args = update_kapal_parser.parse_args()
        new_call_sign = args["new_call_sign"]
        flag = args["flag"]
        kelas = args["kelas"]
        builder = args["builder"]
        year_built = args["year_built"]
        size = args["size"]
        status = args["status"]
        uploaded_file = args["xml_file"]
        
        kapal = Kapal.query.get(call_sign)
        
        if kapal is None:
            raise TypeError("Kapal not found")
        
        kapal.call_sign = new_call_sign
        kapal.flag = flag
        kapal.kelas = kelas
        kapal.builder = builder
        kapal.year_built = year_built
        kapal.size = size
        kapal.status = status

        # Do something with the uploaded file, for example, save it
        allowed_extensions = {"xml"}
        if uploaded_file is not None:
            if(
                "." in uploaded_file.filename
                and uploaded_file.filename.rsplit(".", 1)[1].lower()
                in allowed_extensions
            ):
                # File Name
                current_datetime = datetime.datetime.now()
                str_datetime = current_datetime.strftime("%Y_%m_%d_%H_%M_%S")
                file_name = (
                    f"{str_datetime}_{call_sign}."
                    + uploaded_file.filename.rsplit(".", 1)[1].lower()
                )
                
                if os.path.exists(f"{file_path}{kapal.xml_file}"):
                    os.remove(f"{file_path}{kapal.xml_file}")
                kapal.xml_file = file_name

                db.session.commit()
                # File Uploaded
                uploaded_file.save(file_path + file_name)
                
                return {"message": "Kapal updated successfully."},201
            else:
                return {
                    "message": "Invalid file extension. Allowed extensions: .xml"
                }, 400
        else:
            db.session.commit()
            return {"message": "Kapal updated successfully."},201

    @api_handle_exception
    def delete(self,call_sign):
        kapal = Kapal.query.get(call_sign)
        if kapal:
            db.session.delete(kapal)
            db.session.commit()
            if os.path.exists(f"{file_path}{kapal.xml_file}"):
                os.remove(f"{file_path}{kapal.xml_file}")
            return {"message": "Kapal successfully deleted."}, 201
        return {"message": "Kapal not found."}, 404

    
        
