from . import utils


class An2Cn(object):
    def __init__(self):
        self.conf = utils.get_default_conf()

    def an2cn(self, inputs=None, mode="low"):
        if inputs is not None:
            if mode not in ["low", "up", "rmb"]:
                raise ValueError("mode 仅支持 low up rmb smart 四种！")

            # 将数字转化为字符串
            if not isinstance(inputs, str):
                inputs = self.convert_number_to_string(inputs)

            # 检查数据是否有效
            self.check_inputs_is_valid(inputs)

            # 切割整数部分和小数部分
            split_result = inputs.split(".")
            len_split_result = len(split_result)
            if len_split_result == 1:
                # 不包含小数的输入
                integer_data = split_result[0]
                if mode == "rmb":
                    output = self.integer_convert(integer_data, "up") + "元整"
                else:
                    output = self.integer_convert(integer_data, mode)
            elif len_split_result == 2:
                # 包含小数的输入
                integer_data = split_result[0]
                decimal_data = split_result[1]
                if mode == "rmb":
                    int_data = self.integer_convert(integer_data, "up")
                    dec_data = self.decimal_convert(decimal_data, "up")
                    len_dec_data = len(dec_data)

                    if len_dec_data == 0:
                        output = int_data + "元整"
                    elif len_dec_data == 1:
                        raise ValueError("异常输出：{dec_data}".format(dec_data=dec_data))
                    elif len_dec_data == 2:
                        if dec_data[1] != "零":
                            if int_data == "零":
                                output = dec_data[1] + "角"
                            else:
                                output = int_data + "元" + dec_data[1] + "角"
                        else:
                            output = int_data + "元整"
                    else:
                        if dec_data[1] != "零":
                            if dec_data[2] != "零":
                                if int_data == "零":
                                    output = dec_data[1] + "角" + dec_data[2] + "分"
                                else:
                                    output = int_data + "元" + dec_data[1] + "角" + dec_data[2] + "分"
                            else:
                                if int_data == "零":
                                    output = dec_data[1] + "角"
                                else:
                                    output = int_data + "元" + dec_data[1] + "角"
                        else:
                            if dec_data[2] != "零":
                                if int_data == "零":
                                    output = dec_data[2] + "分"
                                else:
                                    output = int_data + "元" + "零" + dec_data[2] + "分"
                            else:
                                output = int_data + "元整"

                else:
                    output = self.integer_convert(integer_data, mode) + self.decimal_convert(decimal_data, mode)
            else:
                raise ValueError("输入格式错误：{inputs}！".format(inputs=inputs))
        else:
            raise ValueError("输入数据为空！")

        return output

    @staticmethod
    def check_inputs_is_valid(check_data):
        # 检查输入数据是否在规定的字典中
        all_check_keys = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]
        for data in check_data:
            if data not in all_check_keys:
                raise ValueError("输入的数据不在转化范围内：{data}！".format(data=data))

    @staticmethod
    def convert_number_to_string(number_data):
        # python 会自动把 0.00005 转化成 5e-05，因此 str(0.00005) != "0.00005"
        string_data = str(number_data)
        if "e" in string_data:
            string_data_list = string_data.split("e")
            string_key = string_data_list[0]
            string_value = string_data_list[1]
            if string_value[0] == "-":
                string_data = "0." + "0"*(int(string_value[1:])-1) + string_key
            else:
                string_data = string_key + "0"*int(string_value)

        return string_data

    def integer_convert(self, integer_data, mode):
        numeral_list = self.conf["number_{mode}".format(mode=mode)]
        unit_list = self.conf["unit_{mode}".format(mode=mode)]

        # 去除前面的 0，比如 007 => 7
        integer_data = str(int(integer_data))

        len_integer_data = len(integer_data)

        if len_integer_data > len(unit_list):
            raise ValueError("超出数据范围，最长支持 16 位")

        output_an = ""
        for i, d in enumerate(integer_data):
            if int(d):
                output_an += numeral_list[int(d)] + unit_list[len_integer_data - i - 1]
            else:
                if not (len_integer_data - i - 1) % 4:
                    output_an += numeral_list[int(d)] + unit_list[len_integer_data - i - 1]

                if i > 0 and not output_an[-1] == "零":
                    output_an += numeral_list[int(d)]

        output_an = output_an.replace("零零", "零").replace("零万", "万").replace("零亿", "亿").replace("亿万", "亿").strip("零")

        # 解决「一十几」和「壹拾几」问题
        if output_an[:2] in ["一十", "壹拾"]:
            output_an = output_an[1:]

        # 0 - 1 之间的小数
        if not output_an:
            output_an = "零"

        return output_an

    def decimal_convert(self, decimal_data, mode):
        len_decimal_data = len(decimal_data)

        if len_decimal_data > 15:
            print("warning: 小数部分长度为{len_decimal_data}，超过15位有效精度长度，将自动截取前15位！".format(len_decimal_data=len_decimal_data))
            decimal_data = decimal_data[:15]

        if len_decimal_data:
            output_an = "点"
        else:
            output_an = ""

        numeral_list = self.conf["number_{mode}".format(mode=mode)]

        for data in decimal_data:
            output_an += numeral_list[int(data)]

        return output_an
