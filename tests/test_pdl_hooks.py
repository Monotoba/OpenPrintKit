from opk.core import schema as S


def test_pdl_hooks_map_and_named_fields():
    pdl = {
        "pdl_version": "1.0",
        "id": "hooks.test",
        "name": "Hooks Test",
        "firmware": "marlin",
        "kinematics": "cartesian",
        "geometry": {"bed_shape": [[0,0],[200,0],[200,200],[0,200]], "z_height": 200},
        "extruders": [{"nozzle_diameter": 0.4}],
        "gcode": {
            "before_object": ["; prep"],
            "after_layer_change": ["; post layer"],
            "hooks": {
                "before_object": ["M117 Before Object"],
                "monitor.progress_25": ["M117 25%"],
                "env.lights_on": ["M150 R255 G255 B255"],
            }
        }
    }
    S.validate("pdl", pdl)

