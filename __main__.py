from typing import Final, Tuple, Union, Optional

import stage

# if False:
#     from PIL import Image
#     im = Image.new("RGBA", (100, 100))
#     im.save(stage.INSTRUMENT_PATH + 'NO_INSTRUMENT.png')


def create_polygon_from_line(start_x: int, start_y: int, end_x:int, end_y:int, half_width_x: int, half_width_y: int) -> Union[float, Tuple[float, float]]:
    return (start_x - half_width_x, start_y - half_width_y), (end_x - half_width_x, end_y - half_width_y), (end_x + half_width_x, end_y + half_width_y), (start_x + half_width_x, start_y + half_width_y)


if True:
    import json

    with open("example.json", "r") as read_file:
        print("Starting to convert json decoding")
        test_as_dict = json.load(read_file)
        test_as_object: Final[Optional[stage.Hall]] = stage.Hall.from_dict(test_as_dict)
        if test_as_object is not None:
            test_as_object.draw()

    # test_stage: Final[geometry.Dimension] = geometry.Dimension(1300, 900)
    # test_hidden_areas: Final[Sequence[List[Tuple[float, float]]]] = []
    #
    # test: Final[stage.Hall] = stage.Hall("Test_Großsedlitz", test_stage,
    #                                      stage.Rows([None, None, None, None, None, None,
    #                                                 [stage.Row(geometry.ArcAngles(214, 237), None),
    #                                                  stage.Row(geometry.ArcAngles(303, 326), None)]], 50, 100),
    #                                      [(0, 0), (0, 250), (1500, 250), (1500, 0)],
    #                                      test_hidden_areas, sympy.Point(10, 10))
    # test.draw(100)

if False:
    riesa: Final[Hall] = Hall("2021_11_14_Riesa", Dimension(1580, 960),
                          Rows([[Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET,
                                            INSTRUMENT_NOTHING, INSTRUMENT_FLUTE, INSTRUMENT_FLUTE])],
                                [Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET, INSTRUMENT_BASS_CLARINET,
                                            INSTRUMENT_BASSOON, INSTRUMENT_OBOE, INSTRUMENT_OBOE, INSTRUMENT_FLUTE,
                                            INSTRUMENT_SAX])],
                                [Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET, INSTRUMENT_HORN,
                                            INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET,
                                            INSTRUMENT_EUPHONIUM, INSTRUMENT_EUPHONIUM, INSTRUMENT_EUPHONIUM,
                                            INSTRUMENT_TUBA, INSTRUMENT_SAX, INSTRUMENT_SAX])],
                                [Row(RowAngles(190, 205), [INSTRUMENT_CLARINET, INSTRUMENT_HORN]),
                                 Row(RowAngles(226, 314), [INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET,
                                                           INSTRUMENT_TROMBONE, INSTRUMENT_TROMBONE, INSTRUMENT_TROMBONE,
                                                           INSTRUMENT_TROMBONE, INSTRUMENT_TUBA]),
                                 Row(RowAngles(335, 350), [INSTRUMENT_TUBA, INSTRUMENT_SAX])],
                                [Row(RowAngles(203, 203), [INSTRUMENT_CLARINET]),
                                 Row(RowAngles(337, 337), [INSTRUMENT_TUBA])]], 90, 150),
                          ((540, 0), (290, 200), (290, 235), (1290, 235), (1290, 200), (1040, 0)),
                          [((0, 0), (0, 600), (290, 600), (290, 200), (540, 0),
                            (1040, 0), (1290, 200), (1290, 600), (1580, 600),
                            (1580, 0), (0, 0))], sympy.Point(10, 10))
    riesa.draw(150)

if False:
    glauchau: Final[Hall] = Hall("Glauchau", Dimension(920, 1150),
                             Rows([None, None, [Row(RowAngles(210, 330), None)],
                                   [Row(RowAngles(230, 310), None)], [Row(RowAngles(238.5, 301.5), None)]], 70, 150),
                             ((173, 300), (460, 0), (747, 300)),
                             [((0, 480), (460, 0), (0,0)), ((460, 0), (920, 0), (920, 480))], sympy.Point(10, 10))
    glauchau.draw(150)