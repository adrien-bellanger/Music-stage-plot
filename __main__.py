from typing import Final, List, Sequence, Tuple, Union, Optional

import geometry
import stage

if False:
    from PIL import Image
    im = Image.new("RGBA", (100, 100))
    im.save(stage.INSTRUMENT_PATH + 'NO_INSTRUMENT.png')


def create_polygon_from_line(start_x: int, start_y: int, end_x:int, end_y:int, half_width_x: int, half_width_y: int) -> Union[float, Tuple[float, float]]:
    return (start_x - half_width_x, start_y - half_width_y), (end_x - half_width_x, end_y - half_width_y), (end_x + half_width_x, end_y + half_width_y), (start_x + half_width_x, start_y + half_width_y)


if True:
    import json

    with open("example.json", "r") as read_file:
        print("Starting to convert json decoding")
        test_as_dict = json.load(read_file)
        test_as_object: Final[Optional[stage.Hall]] = stage.Hall.from_dict(test_as_dict)
        test_as_object.draw()

    # test_stage: Final[geometry.Dimension] = geometry.Dimension(1300, 900)
    # test_hidden_areas: Final[Sequence[List[Tuple[float, float]]]] = []
    #
    # test: Final[stage.Hall] = stage.Hall("Test_Großsedlitz", test_stage,
    #                                      stage.Rows([None, None, None, None, None, None,
    #                                                 [stage.Row(geometry.ArcAngles(214, 237), None),
    #                                                  stage.Row(geometry.ArcAngles(303, 326), None)]], 50, 100),
    #                                      [(0, 0), (0, 250), (1500, 250), (1500, 0)],
    #                                      test_hidden_areas, geometry.Position(10, 10))
    # test.draw(100)

if False:
    kulturpalast_stage: Final[geometry.Dimension] = geometry.Dimension(2110, 1570)
    kulturpalast_hidden_areas: Final[Sequence[Union[float, Tuple[float, float]]]] = [
        ((0, 0), (0, 250), (665, 0)), ((2110, 0), (2110, 250), (1445, 0))
    ]

if False:
    import math
    bautzen_krone_1m_Wall: Final[int] = int(math.sqrt(2) * 50)
    bautzen_krone_stage: Final[geometry.Dimension] = geometry.Dimension(1700 + bautzen_krone_1m_Wall * 4 * 2, 1410)
    bautzen_krone_middleLength: Final[int] = int(bautzen_krone_stage.length / 2)
    bautzen_krone_hidden_areas: Final[Sequence[Union[float, Tuple[float, float]]]] = [
        ((0, 0), (0, bautzen_krone_stage.width - bautzen_krone_1m_Wall * 4), (bautzen_krone_middleLength, 0)),
        (
            (bautzen_krone_middleLength, 0),
            (bautzen_krone_stage.length, bautzen_krone_stage.width - bautzen_krone_1m_Wall * 4),
            (bautzen_krone_stage.length, 0)),
        (
            (0, bautzen_krone_stage.width), (bautzen_krone_1m_Wall * 4, bautzen_krone_stage.width),
            (0, bautzen_krone_stage.width - bautzen_krone_1m_Wall * 4)),
        (
            (bautzen_krone_stage.length, bautzen_krone_stage.width),
            (bautzen_krone_stage.length - bautzen_krone_1m_Wall * 4, bautzen_krone_stage.width),
            (bautzen_krone_stage.length, bautzen_krone_stage.width - bautzen_krone_1m_Wall * 4)),
        (
            (bautzen_krone_middleLength, 0),
            (bautzen_krone_middleLength - bautzen_krone_1m_Wall * 2, bautzen_krone_1m_Wall * 2),
            (bautzen_krone_middleLength - bautzen_krone_1m_Wall, bautzen_krone_1m_Wall * 3),
            (bautzen_krone_middleLength + bautzen_krone_1m_Wall, bautzen_krone_1m_Wall)),
        (
            (bautzen_krone_middleLength + bautzen_krone_1m_Wall * 6, bautzen_krone_1m_Wall * 6),
            (bautzen_krone_middleLength + bautzen_krone_1m_Wall * (6 - 2), bautzen_krone_1m_Wall * (6 + 2)),
            (bautzen_krone_middleLength + bautzen_krone_1m_Wall * (6 - 1), bautzen_krone_1m_Wall * (6 + 3)),
            (bautzen_krone_middleLength + bautzen_krone_1m_Wall * (6 + 1), bautzen_krone_1m_Wall * (6 + 1))),
        (
            (bautzen_krone_middleLength + bautzen_krone_1m_Wall * 12, bautzen_krone_1m_Wall * 12),
            (bautzen_krone_middleLength + bautzen_krone_1m_Wall * (12 - 2), bautzen_krone_1m_Wall * (12 + 2)),
            (bautzen_krone_middleLength + bautzen_krone_1m_Wall * (12 - 1), bautzen_krone_1m_Wall * (12 + 3)),
            (bautzen_krone_middleLength + bautzen_krone_1m_Wall * (12 + 1), bautzen_krone_1m_Wall * (12 + 1)))
    ]

    bautzen_krone: Final[Hall] = Hall("Test_Bautzen_Krone", bautzen_krone_stage, Rows([None, None, None, None, None, None], 50, 150),
                                      ((0, 0), (0, 420), (bautzen_krone_stage.length, 420), (bautzen_krone_stage.length, 0)),
                                      bautzen_krone_hidden_areas, geometry.Position(10, 10))
    bautzen_krone.draw(100)

if False:
    elsterwerda_stage: Final[Dimension] = Dimension(1330, 600)
    elsterwerda_hidden_areas: Final[Sequence[Union[float, Tuple[float, float]]]] = [
        ((0, 0), (0, 600), (340, 600), (340, 0)),
        ((1330, 0), (1330, 600), (990, 600), (990, 0))
        ]

    elsterwerda_650: Final[Hall] = Hall("2021_11_13_Elsterwerda", elsterwerda_stage + Dimension(0, 650),
                                    Rows([[Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET,
                                                      INSTRUMENT_FLUTE, INSTRUMENT_FLUTE])],
                                          [Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET, INSTRUMENT_BASSOON,
                                                      INSTRUMENT_OBOE, INSTRUMENT_OBOE, INSTRUMENT_FLUTE, INSTRUMENT_SAX])],
                                          [Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET, INSTRUMENT_BASS_CLARINET,
                                                      INSTRUMENT_HORN, INSTRUMENT_HORN,
                                                      INSTRUMENT_EUPHONIUM, INSTRUMENT_EUPHONIUM, INSTRUMENT_EUPHONIUM,
                                                      INSTRUMENT_SAX, INSTRUMENT_SAX])],
                                    [Row(RowAngles(218, 232), [INSTRUMENT_CLARINET]),
                                     Row(RowAngles(248, 292), [INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET,
                                                               INSTRUMENT_TUBA]),
                                     Row(RowAngles(308, 322), [INSTRUMENT_TUBA, INSTRUMENT_TUBA])],
                                    [Row(RowAngles(252, 288), [INSTRUMENT_TRuMPET,
                                                               INSTRUMENT_TROMBONE, INSTRUMENT_TROMBONE, INSTRUMENT_TROMBONE])]
                                    ], 48, 200),
                                    ((340, 0), (340, 210), (990, 210), (990, 0)),
                                    elsterwerda_hidden_areas, Position(10, 10))
    elsterwerda_650.draw(200)

if False:
    plenarsaal: Final[Hall] = Hall("2021_11_07_Plenarsaal", Dimension(1460, 740),
                               Rows([[Row(None, [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET, INSTRUMENT_CLARINET,
                                                 INSTRUMENT_FLUTE, INSTRUMENT_FLUTE])],
                                     [Row(RowAngles(190, 190), [INSTRUMENT_CLARINET]),
                                      Row(RowAngles(215, 305), [INSTRUMENT_CLARINET, INSTRUMENT_BASS_CLARINET,
                                                                INSTRUMENT_BASSOON, INSTRUMENT_OBOE, INSTRUMENT_OBOE]),
                                      Row(RowAngles(325, 350), [INSTRUMENT_PICOLO, INSTRUMENT_SAX])],
                                     [Row(RowAngles(190, 300), [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET,
                                                                INSTRUMENT_HORN, INSTRUMENT_HORN,
                                                                INSTRUMENT_EUPHONIUM, INSTRUMENT_EUPHONIUM]),
                                      Row(RowAngles(318, 350), [INSTRUMENT_TUBA, INSTRUMENT_SAX, INSTRUMENT_SAX])],
                                     [Row(RowAngles(190, 315), [INSTRUMENT_CLARINET, INSTRUMENT_CLARINET,
                                                                INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET,
                                                                INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET,
                                                                INSTRUMENT_TRuMPET, INSTRUMENT_TRuMPET,
                                                                INSTRUMENT_TROMBONE, INSTRUMENT_TROMBONE,
                                                                INSTRUMENT_TROMBONE]),
                                      Row(RowAngles(327, 327), [INSTRUMENT_TUBA]),
                                      Row(RowAngles(337, 350), [INSTRUMENT_TUBA, INSTRUMENT_SAX])]],
                                    100, 150),
                               ((0, 100), (0,400), (400, 0), (100, 0), (100,100)),
                               [((0, 0), (0, 100), (100, 100), (100, 0)), 
                               ((1460, 0), (1240, 0), (1240, 200), (1460, 200)),
                               create_polygon_from_line(0, 460, 260, 460, 0, 2),
                               create_polygon_from_line(0, 605, 260, 605, 0, 2),
                               create_polygon_from_line(260, 460, 260, 605, 2, 0),
                               create_polygon_from_line(260, 540, 675, 505, 0, 2),
                               create_polygon_from_line(675, 505, 1090, 405, 0, 2),
                               create_polygon_from_line(1150, 325, 1460, 325, 0, 2),
                               create_polygon_from_line(1150, 430, 1460, 480, 0, 2)], Position(1240, 10))
    plenarsaal.draw(150)

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
                            (1580, 0), (0, 0))], Position(10, 10))
    riesa.draw(150)

if False:
    glauchau: Final[Hall] = Hall("Glauchau", Dimension(920, 1150),
                             Rows([None, None, [Row(RowAngles(210, 330), None)],
                                   [Row(RowAngles(230, 310), None)], [Row(RowAngles(238.5, 301.5), None)]], 70, 150),
                             ((173, 300), (460, 0), (747, 300)),
                             [((0, 480), (460, 0), (0,0)), ((460, 0), (920, 0), (920, 480))], Position(10, 10))
    glauchau.draw(150)