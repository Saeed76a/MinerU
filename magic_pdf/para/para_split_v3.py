import copy

from magic_pdf.libs.Constants import LINES_DELETED, CROSS_PAGE

LINE_STOP_FLAG = ('.', '!', '?', '。', '！', '？', ')', '）', '"', '”', ':', '：', ';', '；')


def __process_blocks(blocks):

    result = []
    current_group = []

    for i in range(len(blocks)):
        current_block = blocks[i]

        # 如果当前块是 text 类型
        if current_block['type'] == 'text':
            current_block["bbox_fs"] = copy.deepcopy(current_block["bbox"])
            if 'lines' in current_block and len(current_block["lines"]) > 0:
                current_block['bbox_fs'] = [min([line['bbox'][0] for line in current_block['lines']]),
                                            min([line['bbox'][1] for line in current_block['lines']]),
                                            max([line['bbox'][2] for line in current_block['lines']]),
                                            max([line['bbox'][3] for line in current_block['lines']])]
            current_group.append(current_block)

        # 检查下一个块是否存在
        if i + 1 < len(blocks):
            next_block = blocks[i + 1]
            # 如果下一个块不是 text 类型且是 title 或 interline_equation 类型
            if next_block['type'] in ['title', 'interline_equation']:
                result.append(current_group)
                current_group = []

    # 处理最后一个 group
    if current_group:
        result.append(current_group)

    return result


def __merge_2_blocks(block1, block2):
    if len(block1['lines']) > 0:
        first_line = block1['lines'][0]
        line_height = first_line['bbox'][3] - first_line['bbox'][1]
        if abs(block1['bbox_fs'][0] - first_line['bbox'][0]) < line_height/2:
            last_line = block2['lines'][-1]
            if len(last_line['spans']) > 0:
                last_span = last_line['spans'][-1]
                line_height = last_line['bbox'][3] - last_line['bbox'][1]
                if abs(block2['bbox_fs'][2] - last_line['bbox'][2]) < line_height and not last_span['content'].endswith(LINE_STOP_FLAG):
                    if block1['page_num'] != block2['page_num']:
                        for line in block1['lines']:
                            for span in line['spans']:
                                span[CROSS_PAGE] = True
                    block2['lines'].extend(block1['lines'])
                    block1['lines'] = []
                    block1[LINES_DELETED] = True

    return block1, block2


def __para_merge_page(blocks):
    page_text_blocks_groups = __process_blocks(blocks)
    for text_blocks_group in page_text_blocks_groups:
        if len(text_blocks_group) > 1:
            # 倒序遍历
            for i in range(len(text_blocks_group)-1, -1, -1):
                current_block = text_blocks_group[i]
                # 检查是否有前一个块
                if i - 1 >= 0:
                    prev_block = text_blocks_group[i - 1]
                    __merge_2_blocks(current_block, prev_block)
        else:
            continue


def para_split(pdf_info_dict, debug_mode=False):
    all_blocks = []
    for page_num, page in pdf_info_dict.items():
        blocks = copy.deepcopy(page['preproc_blocks'])
        for block in blocks:
            block['page_num'] = page_num
        all_blocks.extend(blocks)

    __para_merge_page(all_blocks)
    for page_num, page in pdf_info_dict.items():
        page['para_blocks'] = []
        for block in all_blocks:
            if block['page_num'] == page_num:
                page['para_blocks'].append(block)


if __name__ == '__main__':
    input_blocks = [{'type': 'text', 'bbox': [19, 79, 285, 95], 'lines': [{'bbox': [21.360000610351562, 81.50750732421875, 287.69000244140625, 93.62750244140625], 'spans': [{'bbox': [21.360000610351562, 81.62750244140625, 170.3000030517578, 93.62750244140625], 'content': '嘉和美康（688246）/计算机', 'type': 'text', 'score': 1.0}, {'bbox': [170.3000030517578, 81.62750244140625, 176.3000030517578, 93.62750244140625], 'content': ' ', 'type': 'text', 'score': 1.0}, {'bbox': [181.22000122070312, 81.50750732421875, 281.8052062988281, 93.50750732421875], 'content': '证券研究报告/公司点评', 'type': 'text', 'score': 1.0}, {'bbox': [281.69000244140625, 81.50750732421875, 287.69000244140625, 93.50750732421875], 'content': ' ', 'type': 'text', 'score': 1.0}], 'index': 0}], 'index': 0, 'page_num': 'page_0', 'bbox_fs': [21.360000610351562, 81.50750732421875, 287.69000244140625, 93.62750244140625]}, {'type': 'title', 'bbox': [18, 109, 124, 123], 'lines': [{'bbox': [21.360000610351562, 101.70799255371094, 98.47967529296875, 116.21743774414062], 'spans': [{'bbox': [21.360000610351562, 101.70799255371094, 98.47967529296875, 116.21743774414062], 'content': '[Table_Industry] ', 'type': 'text', 'score': 1.0}], 'index': 1}, {'bbox': [21.1200008392334, 110.3074951171875, 129.5640106201172, 122.3074951171875], 'spans': [{'bbox': [21.1200008392334, 110.3074951171875, 129.5640106201172, 122.3074951171875], 'content': '评级：买入（维持）', 'type': 'text', 'score': 1.0}], 'index': 2}], 'index': 1.5, 'page_num': 'page_0'}, {'type': 'text', 'bbox': [20, 126, 117, 137], 'lines': [{'bbox': [21.1200008392334, 127.40557861328125, 116.18000030517578, 136.40557861328125], 'spans': [{'bbox': [21.1200008392334, 127.40557861328125, 116.18000030517578, 136.40557861328125], 'content': '市场价格：16.62 元/股', 'type': 'text', 'score': 1.0}], 'index': 3}], 'index': 3, 'page_num': 'page_0', 'bbox_fs': [21.1200008392334, 127.40557861328125, 116.18000030517578, 136.40557861328125]}, {'type': 'text', 'bbox': [19, 144, 158, 172], 'lines': [{'bbox': [21.1200008392334, 144.1099853515625, 86.88600158691406, 156.50299072265625], 'spans': [{'bbox': [21.1200008392334, 146.005615234375, 84.33599853515625, 155.005615234375], 'content': '分析师：闻学臣', 'type': 'text', 'score': 1.0}, {'bbox': [84.38400268554688, 144.1099853515625, 86.88600158691406, 156.50299072265625], 'content': ' ', 'type': 'text', 'score': 1.0}], 'index': 4}, {'bbox': [21.1200008392334, 159.7099609375, 157.9219970703125, 172.10296630859375], 'spans': [{'bbox': [21.1200008392334, 161.6055908203125, 84.33599853515625, 170.6055908203125], 'content': '执业证书编号：', 'type': 'text', 'score': 1.0}, {'bbox': [84.50399780273438, 159.7099609375, 155.45095825195312, 172.10296630859375], 'content': 'S0740519090007', 'type': 'text', 'score': 1.0}, {'bbox': [155.4199981689453, 159.7099609375, 157.9219970703125, 172.10296630859375], 'content': ' ', 'type': 'text', 'score': 1.0}], 'index': 5}], 'index': 4.5, 'page_num': 'page_0', 'bbox_fs': [21.1200008392334, 144.1099853515625, 157.9219970703125, 172.10296630859375]}, {'type': 'text', 'bbox': [18, 194, 157, 241], 'lines': [{'bbox': [21.1200008392334, 193.86497497558594, 86.88600158691406, 206.23097229003906], 'spans': [{'bbox': [21.1200008392334, 195.80560302734375, 84.33599853515625, 204.80560302734375], 'content': '分析师：何柄谕', 'type': 'text', 'score': 1.0}, {'bbox': [84.38400268554688, 193.86497497558594, 86.88600158691406, 206.23097229003906], 'content': ' ', 'type': 'text', 'score': 1.0}], 'index': 6}, {'bbox': [21.1200008392334, 211.07000732421875, 157.9219970703125, 223.4630126953125], 'spans': [{'bbox': [21.1200008392334, 212.96563720703125, 84.33599853515625, 221.96563720703125], 'content': '执业证书编号：', 'type': 'text', 'score': 1.0}, {'bbox': [84.50399780273438, 211.07000732421875, 155.44796752929688, 223.4630126953125], 'content': 'S0740519090003', 'type': 'text', 'score': 1.0}, {'bbox': [155.4199981689453, 211.07000732421875, 157.9219970703125, 223.4630126953125], 'content': ' ', 'type': 'text', 'score': 1.0}], 'index': 7}, {'bbox': [21.1200008392334, 228.0649871826172, 126.84199523925781, 240.4309844970703], 'spans': [{'bbox': [21.1200008392334, 228.0649871826172, 43.73700714111328, 240.4309844970703], 'content': 'Email', 'type': 'text', 'score': 1.0}, {'bbox': [43.79999923706055, 230.005615234375, 52.79999923706055, 239.005615234375], 'content': '：', 'type': 'text', 'score': 1.0}, {'bbox': [52.68000030517578, 228.0649871826172, 124.41200256347656, 240.4309844970703], 'content': 'heby@zts.com.cn', 'type': 'text', 'score': 1.0}, {'bbox': [124.33999633789062, 228.0649871826172, 126.84199523925781, 240.4309844970703], 'content': ' ', 'type': 'text', 'score': 1.0}], 'index': 8}], 'index': 7, 'page_num': 'page_0', 'bbox_fs': [21.1200008392334, 193.86497497558594, 157.9219970703125, 240.4309844970703]}, {'type': 'table', 'bbox': [18, 338, 169, 418], 'blocks': [{'bbox': [18, 356, 169, 418], 'type': 'table_body', 'lines': [{'bbox': [18, 356, 169, 418], 'spans': [{'bbox': [18, 356, 169, 418], 'score': 0.8198961019515991, 'type': 'table', 'image_path': '4123619a2e8de87ebe695a4e7703d09d957670491c939b1050c96bbf4104210e.jpg'}]}]}, {'bbox': [19, 338, 70, 352], 'type': 'table_caption', 'lines': [{'bbox': [21.1200008392334, 335.9779968261719, 85.39967346191406, 350.4874267578125], 'spans': [{'bbox': [21.1200008392334, 335.9779968261719, 85.39967346191406, 350.4874267578125], 'content': '[Table_Profit] ', 'type': 'text', 'score': 1.0}]}]}], 'index': 9.5, 'page_num': 'page_0'}, {'type': 'image', 'bbox': [19, 426, 163, 558], 'blocks': [{'bbox': [21, 452, 163, 558], 'type': 'image_body', 'lines': [{'bbox': [21, 452, 163, 558], 'spans': [{'bbox': [21, 452, 163, 558], 'score': 0.9999651312828064, 'type': 'image', 'image_path': '0e63ab24cdc2ac4cb0c46bf1ff7b9f094c092b9c5707810cbc2b7e30964cf8a1.jpg'}]}]}, {'bbox': [19, 426, 160, 440], 'type': 'image_caption', 'lines': [{'bbox': [21.1200008392334, 427.8774719238281, 165.74000549316406, 439.8774719238281], 'spans': [{'bbox': [21.1200008392334, 427.8774719238281, 165.74000549316406, 439.8774719238281], 'content': '股价与行业-市场走势对比 ', 'type': 'text', 'score': 1.0}]}]}], 'index': 11.5, 'page_num': 'page_0'}, {'type': 'title', 'bbox': [20, 569, 70, 583], 'lines': [{'bbox': [21.1200008392334, 570.70751953125, 75.38400268554688, 582.70751953125], 'spans': [{'bbox': [21.1200008392334, 570.70751953125, 75.38400268554688, 582.70751953125], 'content': '相关报告 ', 'type': 'text', 'score': 1.0}], 'index': 13}], 'index': 13, 'page_num': 'page_0'}, {'type': 'text', 'bbox': [20, 586, 168, 629], 'lines': [{'bbox': [21.1200008392334, 585.9849853515625, 166.1840057373047, 598.3509521484375], 'spans': [{'bbox': [21.1200008392334, 585.9849853515625, 28.661998748779297, 598.3509521484375], 'content': '1 ', 'type': 'text', 'score': 1.0}, {'bbox': [30.239999771118164, 587.9255981445312, 83.76300048828125, 596.9255981445312], 'content': '《嘉和美康（', 'type': 'text', 'score': 1.0}, {'bbox': [83.78399658203125, 585.9849853515625, 113.72698211669922, 598.3509521484375], 'content': '688246', 'type': 'text', 'score': 1.0}, {'bbox': [113.77999877929688, 587.9255981445312, 131.3000030517578, 596.9255981445312], 'content': '）：', 'type': 'text', 'score': 1.0}, {'bbox': [130.82000732421875, 585.9849853515625, 140.74400329589844, 598.3509521484375], 'content': '24', 'type': 'text', 'score': 1.0}, {'bbox': [140.74400329589844, 587.9255981445312, 151.94000244140625, 596.9255981445312], 'content': ' 年', 'type': 'text', 'score': 1.0}, {'bbox': [154.22000122070312, 585.9849853515625, 166.1840057373047, 598.3509521484375], 'content': 'Q1', 'type': 'text', 'score': 1.0}], 'index': 14}, {'bbox': [21.1200008392334, 603.525634765625, 165.1199951171875, 612.525634765625], 'spans': [{'bbox': [21.1200008392334, 603.525634765625, 165.1199951171875, 612.525634765625], 'content': '收入显著改善，医疗大模型产品落地', 'type': 'text', 'score': 1.0}], 'index': 15}, {'bbox': [21.1200008392334, 617.1849975585938, 50.62199783325195, 629.5509643554688], 'spans': [{'bbox': [21.1200008392334, 619.1256103515625, 48.119998931884766, 628.1256103515625], 'content': '良好》', 'type': 'text', 'score': 1.0}, {'bbox': [48.119998931884766, 617.1849975585938, 50.62199783325195, 629.5509643554688], 'content': ' ', 'type': 'text', 'score': 1.0}], 'index': 16}], 'index': 15, 'page_num': 'page_0', 'bbox_fs': [21.1200008392334, 585.9849853515625, 166.1840057373047, 629.5509643554688]}, {'type': 'text', 'bbox': [19, 648, 167, 677], 'lines': [{'bbox': [21.1200008392334, 648.385009765625, 166.21701049804688, 660.7509765625], 'spans': [{'bbox': [21.1200008392334, 648.385009765625, 28.662002563476562, 660.7509765625], 'content': '2 ', 'type': 'text', 'score': 1.0}, {'bbox': [30.1200008392334, 650.3256225585938, 83.51700592041016, 659.3256225585938], 'content': '《嘉和美康（', 'type': 'text', 'score': 1.0}, {'bbox': [83.54399871826172, 648.385009765625, 113.48698425292969, 660.7509765625], 'content': '688246', 'type': 'text', 'score': 1.0}, {'bbox': [113.54000091552734, 650.3256225585938, 166.21701049804688, 659.3256225585938], 'content': '）：收入逐季', 'type': 'text', 'score': 1.0}], 'index': 17}, {'bbox': [21.1200008392334, 663.9849853515625, 153.6020050048828, 676.3509521484375], 'spans': [{'bbox': [21.1200008392334, 665.9255981445312, 111.12000274658203, 674.9255981445312], 'content': '度加速，继续加大医疗', 'type': 'text', 'score': 1.0}, {'bbox': [113.41999816894531, 663.9849853515625, 121.9219970703125, 676.3509521484375], 'content': 'AI', 'type': 'text', 'score': 1.0}, {'bbox': [121.9219970703125, 665.9255981445312, 151.10299682617188, 674.9255981445312], 'content': ' 投入》', 'type': 'text', 'score': 1.0}, {'bbox': [151.10000610351562, 663.9849853515625, 153.6020050048828, 676.3509521484375], 'content': ' ', 'type': 'text', 'score': 1.0}], 'index': 18}], 'index': 17.5, 'page_num': 'page_0', 'bbox_fs': [21.1200008392334, 648.385009765625, 166.21701049804688, 676.3509521484375]}, {'type': 'text', 'bbox': [19, 695, 167, 738], 'lines': [{'bbox': [21.1200008392334, 695.1849975585938, 166.21701049804688, 707.5509643554688], 'spans': [{'bbox': [21.1200008392334, 695.1849975585938, 28.661998748779297, 707.5509643554688], 'content': '3 ', 'type': 'text', 'score': 1.0}, {'bbox': [30.1200008392334, 697.1256103515625, 83.51700592041016, 706.1256103515625], 'content': '《嘉和美康（', 'type': 'text', 'score': 1.0}, {'bbox': [83.54399871826172, 695.1849975585938, 113.48698425292969, 707.5509643554688], 'content': '688246', 'type': 'text', 'score': 1.0}, {'bbox': [113.54000091552734, 697.1256103515625, 166.21701049804688, 706.1256103515625], 'content': '）：回购彰显', 'type': 'text', 'score': 1.0}], 'index': 19}, {'bbox': [21.1200008392334, 710.7849731445312, 160.22000122070312, 723.1509399414062], 'spans': [{'bbox': [21.1200008392334, 712.7255859375, 138.1199951171875, 721.7255859375], 'content': '公司发展信心，公司加大医疗', 'type': 'text', 'score': 1.0}, {'bbox': [140.4199981689453, 710.7849731445312, 148.9219970703125, 723.1509399414062], 'content': 'AI', 'type': 'text', 'score': 1.0}, {'bbox': [148.9219970703125, 712.7255859375, 160.22000122070312, 721.7255859375], 'content': ' 投', 'type': 'text', 'score': 1.0}], 'index': 20}, {'bbox': [21.1200008392334, 726.4049682617188, 41.62199783325195, 738.7709350585938], 'spans': [{'bbox': [21.1200008392334, 728.3455810546875, 39.12000274658203, 737.3455810546875], 'content': '入》', 'type': 'text', 'score': 1.0}, {'bbox': [39.119998931884766, 726.4049682617188, 41.62199783325195, 738.7709350585938], 'content': ' ', 'type': 'text', 'score': 1.0}], 'index': 21}], 'index': 20, 'page_num': 'page_0', 'bbox_fs': [21.1200008392334, 695.1849975585938, 166.21701049804688, 738.7709350585938]}, {'type': 'text', 'bbox': [427, 80, 506, 94], 'lines': [{'bbox': [429.54998779296875, 81.50750732421875, 509.739990234375, 93.50750732421875], 'spans': [{'bbox': [429.54998779296875, 81.50750732421875, 503.8600158691406, 93.50750732421875], 'content': '2024 年8 月28 日', 'type': 'text', 'score': 1.0}, {'bbox': [503.739990234375, 81.50750732421875, 509.739990234375, 93.50750732421875], 'content': ' ', 'type': 'text', 'score': 1.0}], 'index': 22}], 'index': 22, 'page_num': 'page_0', 'bbox_fs': [429.54998779296875, 81.50750732421875, 509.739990234375, 93.50750732421875]}, {'type': 'table', 'bbox': [184, 108, 568, 273], 'blocks': [{'bbox': [184, 124, 568, 249], 'type': 'table_body', 'lines': [{'bbox': [184, 124, 568, 249], 'spans': [{'bbox': [184, 124, 568, 249], 'score': 0.9999539852142334, 'type': 'table', 'image_path': 'feabef6394c4fd70ba64aece3701cd1fc49a0b7deb4ea0693dd63131f182fb9c.jpg'}]}]}, {'bbox': [184, 108, 295, 122], 'type': 'table_caption', 'lines': [{'bbox': [186.5, 110.3074951171875, 294.9320068359375, 122.3074951171875], 'spans': [{'bbox': [186.5, 110.3074951171875, 294.9320068359375, 122.3074951171875], 'content': '公司盈利预测及估值', 'type': 'text', 'score': 1.0}]}]}, {'bbox': [184, 262, 344, 273], 'type': 'table_footnote', 'lines': [{'bbox': [186.5, 262.17498779296875, 343.1300048828125, 274.5409851074219], 'spans': [{'bbox': [186.5, 264.1156005859375, 213.5, 273.1156005859375], 'content': '备注：', 'type': 'text', 'score': 1.0}, {'bbox': [213.52999877929688, 264.1156005859375, 240.52999877929688, 273.1156005859375], 'content': '股价为', 'type': 'text', 'score': 1.0}, {'bbox': [242.80999755859375, 262.17498779296875, 262.8139953613281, 274.5409851074219], 'content': '2024', 'type': 'text', 'score': 1.0}, {'bbox': [262.8139953613281, 264.1156005859375, 274.1300048828125, 273.1156005859375], 'content': ' 年', 'type': 'text', 'score': 1.0}, {'bbox': [276.4100036621094, 262.17498779296875, 281.41400146484375, 274.5409851074219], 'content': '8', 'type': 'text', 'score': 1.0}, {'bbox': [281.41400146484375, 264.1156005859375, 292.6099853515625, 273.1156005859375], 'content': ' 月', 'type': 'text', 'score': 1.0}, {'bbox': [294.8900146484375, 262.17498779296875, 304.93402099609375, 274.5409851074219], 'content': '27', 'type': 'text', 'score': 1.0}, {'bbox': [304.93402099609375, 264.1156005859375, 343.1300048828125, 273.1156005859375], 'content': ' 日收盘价', 'type': 'text', 'score': 1.0}]}]}], 'index': 24, 'page_num': 'page_0'}, {'type': 'title', 'bbox': [180, 285, 230, 300], 'lines': [{'bbox': [186.5, 277.7750244140625, 189.0019989013672, 290.1410217285156], 'spans': [{'bbox': [186.5, 277.7750244140625, 189.0019989013672, 290.1410217285156], 'content': ' ', 'type': 'text', 'score': 1.0}], 'index': 26}, {'bbox': [180.86000061035156, 280.41796875, 183.79568481445312, 294.9273986816406], 'spans': [{'bbox': [180.86000061035156, 280.41796875, 183.79568481445312, 294.9273986816406], 'content': ' ', 'type': 'text', 'score': 1.0}], 'index': 27}, {'bbox': [180.86000061035156, 287.09747314453125, 235.1300048828125, 299.09747314453125], 'spans': [{'bbox': [180.86000061035156, 287.09747314453125, 235.1300048828125, 299.09747314453125], 'content': '投资要点 ', 'type': 'text', 'score': 1.0}], 'index': 28}], 'index': 27, 'page_num': 'page_0'}, {'type': 'text', 'bbox': [198, 302, 578, 331], 'lines': [{'bbox': [201.88999938964844, 302.3030090332031, 575.02001953125, 315.988037109375], 'spans': [{'bbox': [201.88999938964844, 304.45062255859375, 292.0099792480469, 314.41064453125], 'content': '投资事件：公司发布', 'type': 'text', 'score': 1.0}, {'bbox': [294.6499938964844, 302.3030090332031, 316.8507995605469, 315.988037109375], 'content': '2024', 'type': 'text', 'score': 1.0}, {'bbox': [316.8507995605469, 304.45062255859375, 429.3785705566406, 314.41064453125], 'content': ' 年中报：营业收入规模达', 'type': 'text', 'score': 1.0}, {'bbox': [432.07000732421875, 302.3030090332031, 451.5318298339844, 315.988037109375], 'content': '3.00', 'type': 'text', 'score': 1.0}, {'bbox': [451.5318298339844, 304.45062255859375, 524.1190795898438, 314.41064453125], 'content': ' 亿元，同比增长', 'type': 'text', 'score': 1.0}, {'bbox': [525, 303, 556, 314], 'score': 0.82, 'content': '2.92\\%', 'type': 'inline_equation'}, {'bbox': [555.0999755859375, 304.45062255859375, 575.02001953125, 314.41064453125], 'content': '，归', 'type': 'text', 'score': 1.0}], 'index': 29}, {'bbox': [201.88999938964844, 317.9029846191406, 329.118896484375, 331.6676940917969], 'spans': [{'bbox': [201.88999938964844, 320.05059814453125, 271.7195739746094, 330.0106201171875], 'content': '母净利润为亏损', 'type': 'text', 'score': 1.0}, {'bbox': [274.3699951171875, 317.9029846191406, 293.69873046875, 331.5880126953125], 'content': '0.27', 'type': 'text', 'score': 1.0}, {'bbox': [293.69873046875, 320.05059814453125, 326.31951904296875, 330.0106201171875], 'content': ' 亿元。', 'type': 'text', 'score': 1.0}, {'bbox': [326.3500061035156, 317.9527893066406, 329.118896484375, 331.6676940917969], 'content': ' ', 'type': 'text', 'score': 1.0}], 'index': 30}], 'index': 29.5, 'page_num': 'page_0', 'bbox_fs': [201.88999938964844, 302.3030090332031, 575.02001953125, 331.6676940917969]}, {'type': 'text', 'bbox': [199, 349, 576, 425], 'lines': [{'bbox': [201.88999938964844, 351.2506103515625, 574.9908447265625, 361.21063232421875], 'spans': [{'bbox': [201.88999938964844, 351.2506103515625, 574.9908447265625, 361.21063232421875], 'content': '收入小幅增长，毛利率改善。报告期内，公司医疗临床业务、医疗数据业务等业务板', 'type': 'text', 'score': 1.0}], 'index': 31}, {'bbox': [201.88999938964844, 364.7029724121094, 577.1592407226562, 378.38800048828125], 'spans': [{'bbox': [201.88999938964844, 366.8505859375, 331.8081970214844, 376.81060791015625], 'content': '块平稳发展，整体收入规模达', 'type': 'text', 'score': 1.0}, {'bbox': [334.3900146484375, 364.7029724121094, 353.71875, 378.38800048828125], 'content': '3.00', 'type': 'text', 'score': 1.0}, {'bbox': [353.71875, 366.8505859375, 426.17950439453125, 376.81060791015625], 'content': ' 亿元，同比增长', 'type': 'text', 'score': 1.0}, {'bbox': [427, 365, 457, 377], 'score': 0.92, 'content': '2.92\\%', 'type': 'inline_equation'}, {'bbox': [457.17999267578125, 366.8505859375, 577.1592407226562, 376.81060791015625], 'content': '，整体收入实现平稳增长。', 'type': 'text', 'score': 1.0}], 'index': 32}, {'bbox': [201.88999938964844, 382.4505920410156, 580.0416259765625, 392.4106140136719], 'spans': [{'bbox': [201.88999938964844, 382.4505920410156, 580.0416259765625, 392.4106140136719], 'content': '由于公司优化产品结构，改进实施交付管理，公司业务毛利空间有所提升。报告期内，', 'type': 'text', 'score': 1.0}], 'index': 33}, {'bbox': [201.88999938964844, 395.9229736328125, 574.8645629882812, 409.6080017089844], 'spans': [{'bbox': [201.88999938964844, 398.0705871582031, 291.7491149902344, 408.0306091308594], 'content': '公司综合毛利率达到', 'type': 'text', 'score': 1.0}, {'bbox': [293, 397, 328, 409], 'score': 0.89, 'content': '48.03\\%', 'type': 'inline_equation'}, {'bbox': [328.2699890136719, 398.0705871582031, 386.6952819824219, 408.0306091308594], 'content': '，去年同期为', 'type': 'text', 'score': 1.0}, {'bbox': [388, 397, 423, 409], 'score': 0.89, 'content': '45.52\\%', 'type': 'inline_equation'}, {'bbox': [423.30999755859375, 398.0705871582031, 471.7752990722656, 408.0306091308594], 'content': '，同比提升', 'type': 'text', 'score': 1.0}, {'bbox': [474.3399963378906, 395.9229736328125, 493.80181884765625, 409.6080017089844], 'content': '2.51', 'type': 'text', 'score': 1.0}, {'bbox': [493.80181884765625, 398.0705871582031, 574.8645629882812, 408.0306091308594], 'content': ' 个百分点，公司毛', 'type': 'text', 'score': 1.0}], 'index': 34}, {'bbox': [201.88999938964844, 411.5229797363281, 279.6589050292969, 425.2080078125], 'spans': [{'bbox': [201.88999938964844, 413.67059326171875, 271.7195739746094, 423.630615234375], 'content': '利率明显改善。', 'type': 'text', 'score': 1.0}, {'bbox': [271.7300109863281, 411.5229797363281, 279.6589050292969, 425.2080078125], 'content': '  ', 'type': 'text', 'score': 1.0}], 'index': 35}], 'index': 33, 'page_num': 'page_0'}, {'type': 'text', 'bbox': [199, 427, 577, 503], 'lines': [{'bbox': [201.88999938964844, 429.2705993652344, 574.9743041992188, 439.2306213378906], 'spans': [{'bbox': [201.88999938964844, 429.2705993652344, 574.9743041992188, 439.2306213378906], 'content': '降本增效成效显著，管理、销售费用率下降。报告期内，公司注重内控管理、人员能', 'type': 'text', 'score': 1.0}], 'index': 36}, {'bbox': [201.88999938964844, 442.7229919433594, 575.1400146484375, 456.40802001953125], 'spans': [{'bbox': [201.88999938964844, 444.87060546875, 530.7092895507812, 454.83062744140625], 'content': '效提升，加强管理方式优化及费用控制，公司运营管理方面降本增效明显。', 'type': 'text', 'score': 1.0}, {'bbox': [530.3800048828125, 442.7229919433594, 552.600830078125, 456.40802001953125], 'content': '2024', 'type': 'text', 'score': 1.0}, {'bbox': [552.600830078125, 444.87060546875, 575.1400146484375, 454.83062744140625], 'content': ' 年上', 'type': 'text', 'score': 1.0}], 'index': 37}, {'bbox': [201.88999938964844, 458.3229675292969, 575.1334838867188, 472.00799560546875], 'spans': [{'bbox': [201.88999938964844, 460.4705810546875, 310.71295166015625, 470.43060302734375], 'content': '半年，公司销售费用率为', 'type': 'text', 'score': 1.0}, {'bbox': [312, 459, 348, 471], 'score': 0.91, 'content': '16.39\\%', 'type': 'inline_equation'}, {'bbox': [347.3500061035156, 460.4705810546875, 406.1438293457031, 470.43060302734375], 'content': '，去年同期为', 'type': 'text', 'score': 1.0}, {'bbox': [407, 459, 443, 471], 'score': 0.9, 'content': '17.57\\%', 'type': 'inline_equation'}, {'bbox': [442.75, 460.4705810546875, 501.5438232421875, 470.43060302734375], 'content': '，同比下降个', 'type': 'text', 'score': 1.0}, {'bbox': [504.2200012207031, 458.3229675292969, 523.5487670898438, 472.00799560546875], 'content': '1.18', 'type': 'text', 'score': 1.0}, {'bbox': [523.5487670898438, 460.4705810546875, 575.1334838867188, 470.43060302734375], 'content': ' 百分点；管', 'type': 'text', 'score': 1.0}], 'index': 38}, {'bbox': [201.88999938964844, 473.9229736328125, 575.0936279296875, 487.6080017089844], 'spans': [{'bbox': [201.88999938964844, 476.0705871582031, 251.79959106445312, 486.0306091308594], 'content': '理费用率为', 'type': 'text', 'score': 1.0}, {'bbox': [253, 474, 288, 487], 'score': 0.89, 'content': '16.21\\%', 'type': 'inline_equation'}, {'bbox': [288.2900085449219, 476.0705871582031, 346.8248596191406, 486.0306091308594], 'content': '，去年同期为', 'type': 'text', 'score': 1.0}, {'bbox': [348, 474, 384, 487], 'score': 0.89, 'content': '17.79\\%', 'type': 'inline_equation'}, {'bbox': [383.3500061035156, 476.0705871582031, 431.9348449707031, 486.0306091308594], 'content': '，同比下降', 'type': 'text', 'score': 1.0}, {'bbox': [434.5899963378906, 473.9229736328125, 453.9187316894531, 487.6080017089844], 'content': '1.58', 'type': 'text', 'score': 1.0}, {'bbox': [453.9187316894531, 476.0705871582031, 575.0936279296875, 486.0306091308594], 'content': ' 个百分点。公司管理费用率', 'type': 'text', 'score': 1.0}], 'index': 39}, {'bbox': [201.88999938964844, 489.5727844238281, 434.7189025878906, 503.2876892089844], 'spans': [{'bbox': [201.88999938964844, 491.67059326171875, 431.7367858886719, 501.630615234375], 'content': '及销售费用率均实现下降，公司运营效率明显提升。', 'type': 'text', 'score': 1.0}, {'bbox': [431.95001220703125, 489.5727844238281, 434.7189025878906, 503.2876892089844], 'content': ' ', 'type': 'text', 'score': 1.0}], 'index': 40}], 'index': 38, 'page_num': 'page_0'}, {'type': 'text', 'bbox': [199, 505, 577, 628], 'lines': [{'bbox': [201.88999938964844, 505.1727600097656, 575.0682983398438, 518.8876953125], 'spans': [{'bbox': [201.88999938964844, 507.27056884765625, 241.9491424560547, 517.2305908203125], 'content': '公司加大', 'type': 'text', 'score': 1.0}, {'bbox': [245.2100067138672, 505.1727600097656, 255.1788787841797, 518.8876953125], 'content': 'AI', 'type': 'text', 'score': 1.0}, {'bbox': [255.1788787841797, 507.27056884765625, 328.44818115234375, 517.2305908203125], 'content': ' 投入力度，医疗', 'type': 'text', 'score': 1.0}, {'bbox': [331.75, 505.1727600097656, 341.7189025878906, 518.8876953125], 'content': 'AI', 'type': 'text', 'score': 1.0}, {'bbox': [341.7189025878906, 507.27056884765625, 575.0682983398438, 517.2305908203125], 'content': ' 产品落地情况良好。公司继续加大研发投入力度，尤', 'type': 'text', 'score': 1.0}], 'index': 41}, {'bbox': [201.88999938964844, 520.7230224609375, 575.057861328125, 534.4080200195312], 'spans': [{'bbox': [201.88999938964844, 522.87060546875, 241.83958435058594, 532.8306274414062], 'content': '其是医疗', 'type': 'text', 'score': 1.0}, {'bbox': [244.97000122070312, 520.7230224609375, 254.45889282226562, 534.4080200195312], 'content': 'AI', 'type': 'text', 'score': 1.0}, {'bbox': [254.45889282226562, 522.87060546875, 407.5176696777344, 532.8306274414062], 'content': ' 投入力度。报告期内，公司新申请', 'type': 'text', 'score': 1.0}, {'bbox': [410.8299865722656, 520.7230224609375, 421.8876953125, 534.4080200195312], 'content': '26', 'type': 'text', 'score': 1.0}, {'bbox': [421.8876953125, 522.87060546875, 575.057861328125, 532.8306274414062], 'content': ' 项发明专利，主要集中在医疗数据', 'type': 'text', 'score': 1.0}], 'index': 42}, {'bbox': [201.88999938964844, 536.322998046875, 574.8896484375, 550.0079956054688], 'spans': [{'bbox': [201.88999938964844, 538.4705810546875, 231.77001953125, 548.4306030273438], 'content': '利用和', 'type': 'text', 'score': 1.0}, {'bbox': [234.77000427246094, 536.322998046875, 244.13890075683594, 550.0079956054688], 'content': 'AI', 'type': 'text', 'score': 1.0}, {'bbox': [244.13890075683594, 538.4705810546875, 306.98907470703125, 548.4306030273438], 'content': ' 领域，并获得', 'type': 'text', 'score': 1.0}, {'bbox': [309.8900146484375, 536.322998046875, 315.4277648925781, 550.0079956054688], 'content': '1', 'type': 'text', 'score': 1.0}, {'bbox': [315.4277648925781, 538.4705810546875, 368.31951904296875, 548.4306030273438], 'content': ' 项核心技术', 'type': 'text', 'score': 1.0}, {'bbox': [368.3500061035156, 538.013427734375, 371.6667785644531, 549.140625], 'content': '“', 'type': 'text', 'score': 1.0}, {'bbox': [371.7099914550781, 538.4705810546875, 521.548095703125, 548.4306030273438], 'content': '大模型辅助电子病历自动生成技术', 'type': 'text', 'score': 1.0}, {'bbox': [521.6199951171875, 538.013427734375, 524.936767578125, 549.140625], 'content': '”', 'type': 'text', 'score': 1.0}, {'bbox': [524.97998046875, 538.4705810546875, 574.8896484375, 548.4306030273438], 'content': '。依托公司', 'type': 'text', 'score': 1.0}], 'index': 43}, {'bbox': [201.88999938964844, 551.9229736328125, 574.925048828125, 565.6080322265625], 'spans': [{'bbox': [201.88999938964844, 551.9229736328125, 211.25889587402344, 565.6080322265625], 'content': 'AI', 'type': 'text', 'score': 1.0}, {'bbox': [211.25889587402344, 554.0706176757812, 332.65252685546875, 564.0306396484375], 'content': ' 技术的积累，公司推出医疗', 'type': 'text', 'score': 1.0}, {'bbox': [335.2300109863281, 551.9229736328125, 344.5989074707031, 565.6080322265625], 'content': 'AI', 'type': 'text', 'score': 1.0}, {'bbox': [344.5989074707031, 554.0706176757812, 574.925048828125, 564.0306396484375], 'content': ' 应用开发平台，打造全院智慧化服务接入底座，实现', 'type': 'text', 'score': 1.0}], 'index': 44}, {'bbox': [201.88999938964844, 567.552978515625, 574.8896484375, 581.238037109375], 'spans': [{'bbox': [201.88999938964844, 569.7006225585938, 291.7491149902344, 579.66064453125], 'content': '多技术框架、多业务', 'type': 'text', 'score': 1.0}, {'bbox': [294.4100036621094, 567.552978515625, 303.7789001464844, 581.238037109375], 'content': 'AI', 'type': 'text', 'score': 1.0}, {'bbox': [303.7789001464844, 569.7006225585938, 356.19952392578125, 579.66064453125], 'content': ' 应用接入。', 'type': 'text', 'score': 1.0}, {'bbox': [356.3500061035156, 567.552978515625, 378.5508117675781, 581.238037109375], 'content': '2024', 'type': 'text', 'score': 1.0}, {'bbox': [378.5508117675781, 569.7006225585938, 391.0299987792969, 579.66064453125], 'content': ' 年', 'type': 'text', 'score': 1.0}, {'bbox': [393.54998779296875, 567.552978515625, 399.0877380371094, 581.238037109375], 'content': '7', 'type': 'text', 'score': 1.0}, {'bbox': [399.0877380371094, 569.7006225585938, 531.5186157226562, 579.66064453125], 'content': ' 月，公司与北医三院联合发布', 'type': 'text', 'score': 1.0}, {'bbox': [531.5800170898438, 569.2434692382812, 534.8967895507812, 580.3706665039062], 'content': '“', 'type': 'text', 'score': 1.0}, {'bbox': [534.9400024414062, 569.7006225585938, 574.8896484375, 579.66064453125], 'content': '三生大模', 'type': 'text', 'score': 1.0}], 'index': 45}, {'bbox': [201.88999938964844, 583.1529541015625, 575.1400146484375, 596.8380126953125], 'spans': [{'bbox': [201.88999938964844, 585.3005981445312, 211.85000610351562, 595.2606201171875], 'content': '型', 'type': 'text', 'score': 1.0}, {'bbox': [211.85000610351562, 584.8434448242188, 215.16676330566406, 595.9706420898438], 'content': '”', 'type': 'text', 'score': 1.0}, {'bbox': [215.2100067138672, 585.3005981445312, 540.5800170898438, 595.2606201171875], 'content': '，以大模型为底座的多业务场景得到落地验证并且应用效果良好，比如新型', 'type': 'text', 'score': 1.0}, {'bbox': [543.219970703125, 583.1529541015625, 552.5888671875, 596.8380126953125], 'content': 'AI', 'type': 'text', 'score': 1.0}, {'bbox': [552.5888671875, 585.3005981445312, 575.1400146484375, 595.2606201171875], 'content': ' 产品', 'type': 'text', 'score': 1.0}], 'index': 46}, {'bbox': [201.88999938964844, 600.9005737304688, 575.1082763671875, 610.860595703125], 'spans': [{'bbox': [201.88999938964844, 600.9005737304688, 575.1082763671875, 610.860595703125], 'content': '可以将医务人员曾经数小时的病历书写工作缩减至半小时内完成，大幅提升书写内容', 'type': 'text', 'score': 1.0}], 'index': 47}, {'bbox': [201.88999938964844, 614.4027709960938, 304.618896484375, 628.1177368164062], 'spans': [{'bbox': [201.88999938964844, 616.5006103515625, 301.7195129394531, 626.4606323242188], 'content': '的准确率及工作效率。', 'type': 'text', 'score': 1.0}, {'bbox': [301.8500061035156, 614.4027709960938, 304.618896484375, 628.1177368164062], 'content': ' ', 'type': 'text', 'score': 1.0}], 'index': 48}], 'index': 44.5, 'page_num': 'page_0'}, {'type': 'text', 'bbox': [200, 646, 577, 690], 'lines': [{'bbox': [201.88999938964844, 645.552978515625, 574.8973999023438, 659.238037109375], 'spans': [{'bbox': [201.88999938964844, 647.7006225585938, 310.00994873046875, 657.66064453125], 'content': '投资建议：我们预计公司', 'type': 'text', 'score': 1.0}, {'bbox': [312.5299987792969, 645.552978515625, 384.72003173828125, 659.238037109375], 'content': '2024/2025/2026', 'type': 'text', 'score': 1.0}, {'bbox': [384.72003173828125, 647.7006225585938, 447.2890625, 657.66064453125], 'content': ' 年收入分别为', 'type': 'text', 'score': 1.0}, {'bbox': [449.8299865722656, 645.552978515625, 526.9088745117188, 659.238037109375], 'content': '9.03/11.48/14.47 ', 'type': 'text', 'score': 1.0}, {'bbox': [526.9000244140625, 647.7006225585938, 574.8973999023438, 657.66064453125], 'content': '亿元，净利', 'type': 'text', 'score': 1.0}], 'index': 49}, {'bbox': [201.88999938964844, 661.1529541015625, 574.98876953125, 674.8380126953125], 'spans': [{'bbox': [201.88999938964844, 663.3005981445312, 241.7300262451172, 673.2606201171875], 'content': '润分别为', 'type': 'text', 'score': 1.0}, {'bbox': [241.85000610351562, 661.1529541015625, 311.3388977050781, 674.8380126953125], 'content': ' 0.95/1.20/1.60 ', 'type': 'text', 'score': 1.0}, {'bbox': [311.3299865722656, 663.3005981445312, 361.239501953125, 673.2606201171875], 'content': '亿元，对应', 'type': 'text', 'score': 1.0}, {'bbox': [364.989990234375, 661.1529541015625, 378.35333251953125, 674.8380126953125], 'content': 'PE', 'type': 'text', 'score': 1.0}, {'bbox': [378.35333251953125, 663.3005981445312, 411.8995361328125, 673.2606201171875], 'content': ' 分别为', 'type': 'text', 'score': 1.0}, {'bbox': [411.9100036621094, 661.1529541015625, 481.42193603515625, 674.8380126953125], 'content': '  24.1/19.0/14.3', 'type': 'text', 'score': 1.0}, {'bbox': [481.42193603515625, 663.3005981445312, 574.98876953125, 673.2606201171875], 'content': ' 倍。考虑公司业绩高', 'type': 'text', 'score': 1.0}], 'index': 50}, {'bbox': [201.88999938964844, 676.802734375, 431.35888671875, 690.5177001953125], 'spans': [{'bbox': [201.88999938964844, 678.9005737304688, 371.7577209472656, 688.860595703125], 'content': '增长以及估值处于较低水平，给予公司', 'type': 'text', 'score': 1.0}, {'bbox': [371.8299865722656, 678.4434204101562, 375.1467590332031, 689.5706176757812], 'content': '“', 'type': 'text', 'score': 1.0}, {'bbox': [375.19000244140625, 678.9005737304688, 395.1099853515625, 688.860595703125], 'content': '买入', 'type': 'text', 'score': 1.0}, {'bbox': [395.1099853515625, 678.4434204101562, 398.4267578125, 689.5706176757812], 'content': '”', 'type': 'text', 'score': 1.0}, {'bbox': [398.4700012207031, 678.9005737304688, 428.45953369140625, 688.860595703125], 'content': '评级。', 'type': 'text', 'score': 1.0}, {'bbox': [428.5899963378906, 676.802734375, 431.35888671875, 690.5177001953125], 'content': ' ', 'type': 'text', 'score': 1.0}], 'index': 51}], 'index': 50, 'page_num': 'page_0'}, {'type': 'text', 'bbox': [200, 708, 404, 721], 'lines': [{'bbox': [201.88999938964844, 708.0027465820312, 404.9588928222656, 721.7177124023438], 'spans': [{'bbox': [201.88999938964844, 710.1005859375, 402.00811767578125, 720.0606079101562], 'content': '风险提示：业务发展不及预期，政策推进缓慢', 'type': 'text', 'score': 1.0}, {'bbox': [402.19000244140625, 708.0027465820312, 404.9588928222656, 721.7177124023438], 'content': ' ', 'type': 'text', 'score': 1.0}], 'index': 52}], 'index': 52, 'page_num': 'page_0'}]
    # 调用函数
    groups = __process_blocks(input_blocks)
    for group_index, group in enumerate(groups):
        print(f"Group {group_index}: {group}")
