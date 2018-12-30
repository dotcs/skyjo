import json
import numpy as np


class NumpyEncoder(json.JSONEncoder):
    int_types = (
        np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64
    )
    float_types = (
        np.float_, np.float16, np.float32, np.float64, np.float128
    )
    bool_types = (np.bool_,)
    tolist_types = (np.ndarray,)

    def default(self, obj):
        if isinstance(obj, self.int_types):
            return int(obj)
        if isinstance(obj, self.float_types):
            return float(obj)
        if isinstance(obj, self.bool_types):
            return bool(obj)
        if isinstance(obj, self.tolist_types):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
