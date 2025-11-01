from opk.core import schema as S


def test_pdl_extruders_abl_valid():
    pdl = {
        "pdl_version": "1.0",
        "id": "voron_24_350",
        "name": "Voron 2.4 350",
        "firmware": "klipper",
        "kinematics": "corexy",
        "geometry": {
            "bed_shape": [[0,0],[350,0],[350,350],[0,350]],
            "z_height": 350,
            "origin": "front_left"
        },
        "extruders": [
            {"id":"E0","nozzle_diameter":0.4,"nozzle_type":"hardened_steel","drive":"direct","max_nozzle_temperature": 300},
            {"id":"E1","nozzle_diameter":0.6,"nozzle_type":"brass","drive":"direct","max_nozzle_temperature": 300}
        ],
        "multi_material": {"spool_banks": [{"name":"AMS-1","capacity":4}]},
        "features": {"auto_bed_leveling": True, "probe":{"type":"inductive","mesh_size":[7,7]}}
    }
    S.validate("pdl", pdl)

def test_pdl_with_materials():
    pdl = {
        "pdl_version": "1.0",
        "id": "mat.test",
        "name": "Materials Test",
        "firmware": "marlin",
        "kinematics": "cartesian",
        "geometry": {"bed_shape": [[0,0],[220,0],[220,220],[0,220]], "z_height": 220},
        "extruders": [{"nozzle_diameter": 0.4}],
        "materials": [
            {"name": "PLA", "filament_type": "PLA", "filament_diameter": 1.75, "nozzle_temperature": 205, "bed_temperature": 60,
             "retraction_length": 0.8, "retraction_speed": 40, "fan_speed": 100, "color_hex": "#FFFFFF"}
        ]
    }
    S.validate("pdl", pdl)
