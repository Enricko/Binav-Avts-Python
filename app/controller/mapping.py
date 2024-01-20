import os
import datetime
from flask_restx import Resource,reqparse
from app.extensions import api_handle_exception,db
from app.model.mapping import Mapping
from app.api_model.mapping import get_mapping_model,insert_mapping_parser,update_mapping_parser
from app.resources import ns


# Uploaded file path
file_path = "assets/mapping/"

# Pagination parameters
pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument("page", type=int, help="Page number", default=1)
pagination_parser.add_argument("per_page", type=int, help="Items per page", default=10)

@ns.route('/mapping')
class MappingList(Resource):
    @ns.marshal_list_with(get_mapping_model)
    @ns.expect(pagination_parser)
    @api_handle_exception
    def get(self):
        args = pagination_parser.parse_args()
        page = args["page"]
        per_page = args["per_page"]
        offset = (page - 1) * per_page

        total_count = Mapping.query.count()

        mapping = Mapping.query.offset(offset).limit(per_page).all()

        return {
            "message": "Data Mapping Ditemukan",
            "status": 200,
            "page": page,
            "perpage": per_page,
            "total": total_count,
            "data": mapping,
        }, 200
        
    @ns.expect(insert_mapping_parser)
    @api_handle_exception
    def post(self):
        args = insert_mapping_parser.parse_args()
        id_client = args["id_client"]
        name = args["name"]
        switch = args["switch"]
        uploaded_file = args["file"]

        # Do something with the uploaded file, for example, save it
        allowed_extensions = {"kml","kmz"}
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
                    f"{str_datetime}_{name}."
                    + uploaded_file.filename.rsplit(".", 1)[1].lower()
                )

                # Upload Kapal
                kapal = Mapping(
                    id_client=id_client,
                    name=name,
                    switch=switch,
                    file=file_name,
                )

                db.session.add(kapal)

                db.session.commit()

                # File Uploaded
                uploaded_file.save(file_path + file_name)
                
                return {"message": "Mapping uploaded successfully."},201
            else:
                return {
                    "message": "Invalid file extension. Allowed extensions: .kml , .kmz"
                }, 400
        else:
            return {
                "message": "file field is required."
            }, 400
        
@ns.route("/mapping/<string:id_mapping>")
class MappingData(Resource):
    @ns.marshal_list_with(get_mapping_model)
    @api_handle_exception
    def get(self,id_mapping):
        mapping = Mapping.query.get(id_mapping)

        return {
            "message": "Data Mapping Ditemukan",
            "status": 200,
            "page": 1,
            "perpage": 1,
            "total": 1,
            "data": mapping,
        }, 200
        
    @ns.expect(update_mapping_parser)
    @api_handle_exception
    def post(self,id_mapping):
        args = insert_mapping_parser.parse_args()
        name = args["name"]
        switch = args["switch"]
        uploaded_file = args["file"]
        
        mapping = Mapping.query.get(id_mapping)
        
        mapping.name = name
        mapping.switch = switch

        # Do something with the uploaded file, for example, save it
        allowed_extensions = {"kml","kmz"}
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
                    f"{str_datetime}_{name}."
                    + uploaded_file.filename.rsplit(".", 1)[1].lower()
                )
                
                if os.path.exists(f"{file_path}{mapping.file}"):
                    os.remove(f"{file_path}{mapping.file}")
                mapping.file = file_name

                db.session.commit()

                # File Uploaded
                uploaded_file.save(file_path + file_name)
                
                return {"message": "Mapping uploaded successfully."},201
            else:
                return {
                    "message": "Invalid file extension. Allowed extensions: .kml , .kmz"
                }, 400
        else:
            db.session.commit()
            return {"message": "Mapping updated successfully."},201
        
    @api_handle_exception
    def delete(self,id_mapping):
        mapping = Mapping.query.get(id_mapping)
        db.session.delete(mapping)
        db.session.commit()
        if os.path.exists(f"{file_path}{mapping.file}"):
            os.remove(f"{file_path}{mapping.file}")
        return {"message": "Mapping successfully deleted."}, 201