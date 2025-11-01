from opk.core import schema as S


def test_pdl_with_gcode_blocks():
    pdl = {
        "pdl_version": "1.0",
        "id": "mk3s",
        "name": "Prusa MK3S",
        "firmware": "marlin",
        "kinematics": "cartesian",
        "geometry": {
            "bed_shape": [[0,0],[250,0],[250,210],[0,210]],
            "z_height": 210
        },
        "extruders": [{"id":"E0","nozzle_diameter":0.4}],
        "gcode": {
            "start": [
                "M140 S{bed}",
                "M104 S{nozzle}",
                "G28",
                "G92 E0"
            ],
            "end": [
                "M104 S0",
                "M140 S0",
                "G1 X0 Y200 F3000",
                "M84"
            ],
            "tool_change": ["; T{tool} change"],
            "layer_change": ["; Layer {layer}"]
        }
    }
    S.validate("pdl", pdl)

