spelunker_state = {
    "dimensions": {"x": [4e-9, "m"], "y": [4e-9, "m"], "z": [4e-8, "m"]},
    "crossSectionScale": 0.5,
    "layers": [
        {
            "type": "image",
            "source": "",
            "tab": "source",
            "shader": "#uicontrol float black slider(min=0, max=1, default=0.0)\n#uicontrol float white slider(min=0, max=1, default=1.0)\nfloat rescale(float value) {\n  return (value - black) / (white - black);\n}\nvoid main() {\n  float val = toNormalized(getDataValue());\n  if (val < black) {\n    emitRGB(vec3(0,0,0));\n  } else if (val > white) {\n    emitRGB(vec3(1.0, 1.0, 1.0));\n  } else {\n    emitGrayscale(rescale(val));\n  }\n}\n",
            "name": "img",
        },
        {"type": "segmentation", "source": "", "tab": "source", "name": "seg"},
        {
            "type": "annotation",
            "source": "local://annotations",
            "tab": "source",
            "annotations": [],
            "name": "ann",
        },
    ],
    "showSlices": False,
    "selectedLayer": {"visible": True, "layer": "seg"},
    "layout": "xy-3d",
}
