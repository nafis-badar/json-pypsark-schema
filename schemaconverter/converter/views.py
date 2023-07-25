from django.shortcuts import render
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt


def prepare_from_object(obj):  
    if isinstance(obj, str):
        return "StringType()"
    elif isinstance(obj, int) or isinstance(obj, float):
        return "IntegerType()"
    elif not isinstance(obj, dict):
        return None
    elif obj is None:
        return "StringType()"

    schema = "StructType([0])"
    field_names = list(obj.keys())
    schema_str = []

    for v in field_names:
        if isinstance(obj[v], str):
            schema_str.append(f"StructField('{v}', StringType(), True)")
        elif isinstance(obj[v], bool):
            schema_str.append(f"StructField('{v}', BooleanType(), True)")
        elif isinstance(obj[v], int) or isinstance(obj[v], float):
            schema_str.append(f"StructField('{v}', IntegerType(), True)")
        elif isinstance(obj[v], list):
            array_schema = f"StructField('{v}', ArrayType(0), True)"
            get_new_schema = prepare_from_object(obj[v][0])
            array_schema = array_schema.replace("0", get_new_schema)
            schema_str.append(array_schema)
        elif isinstance(obj[v], dict):
            obj_schema = prepare_from_object(obj[v])
            obj_schema_inside_struct_field = f"StructField('{v}', {obj_schema}, True)"
            schema_str.append(obj_schema_inside_struct_field)

    schema = schema.replace("0", ",".join(schema_str))

    return schema

def index(request):
     return render(request, 'index.html')


@csrf_exempt
def info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        if data is not None and len(data) > 0:
            response_data= prepare_from_object(data)
            print(response_data)
            return HttpResponse(response_data,
                                content_type='application/json', status=200)
        else:
            return HttpResponse(json.dumps({"status": 0, "data": "something went wrong"}),
                                content_type='application/json', status=404)
    else:
        return HttpResponse(json.dumps({"status": 0, "data": "method not allowed"}),
                            content_type='application/json', status=405)


