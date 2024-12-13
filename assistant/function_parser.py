import functools
import inspect
import re

def type_mapping(dtype):
    if dtype == float:
        return "number"
    elif dtype == int:
        return "integer"
    elif dtype == str:
        return "string"
    else:
        return "string"

def extract_params(doc_str: str):
    params_str = [line for line in doc_str.split("\n") if line.strip()]
    params = {}
    for line in params_str:
        if line.strip().startswith(':param'):
            param_match = re.findall(r'(?<=:param )\w+', line)
            if param_match:
                param_name = param_match[0]
                desc_match = line.replace(f":param {param_name}:", "").strip()
                if desc_match:
                    params[param_name] = desc_match
    return params

def parse_function_to_schema(func):
    if isinstance(func, functools.partial) or isinstance(func, functools.partialmethod):
        fixed_args = func.keywords
        _func = func.func
        if isinstance(func, functools.partial) and (fixed_args is None or fixed_args == {}):
            fixed_args = dict(zip(func.func.__code__.co_varnames, func.args))
    else:
        fixed_args = {}
        _func = func

    func_name = _func.__name__
    argspec = inspect.getfullargspec(_func)
    func_doc = inspect.getdoc(_func)
    func_description = ''.join([line for line in func_doc.split("\n") if not line.strip().startswith(':')])
    param_details = extract_params(func_doc) if func_doc else {}

    params = {}
    for param_name in argspec.args:
        if param_name not in fixed_args.keys():
            params[param_name] = {
                "description": param_details.get(param_name) or "",
                "type": type_mapping(argspec.annotations.get(param_name, type(None)))
            }

    _required = [i for i in argspec.args if i not in fixed_args.keys()]
    if inspect.getfullargspec(_func).defaults:
        _required = [argspec.args[i] for i, a in enumerate(argspec.args) if
                     argspec.args[i] not in inspect.getfullargspec(_func).defaults and argspec.args[
                         i] not in fixed_args.keys()]

    return {
        "name": func_name,
        "description": func_description,
        "parameters": {
            "type": "object",
            "properties": params
        },
        "required": _required
    }
