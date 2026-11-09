from Nexa import jsonify

def RaiseJSONErr(ERR,CDE,**info):
    return jsonify({"success":False,
                    "error":ERR,
                    "statusCDE":CDE,
                    "info":info},CDE)