import rjsmin

with open("html5kellycolorpicker.js", "r") as f:
    js_code = f.read()

minified_js = rjsmin.jsmin(js_code)

with open("html5kellycolorpicker.min.js", "w") as f:
    f.write(minified_js)
