package main

//#include <stdlib.h>
import "C"

import (
	"bytes"
	"errors"
	"sort"
	"unsafe"
	"strings"
)

var encodings = map[string]map[uint16]rune{}


func addEncoding(encodingName string, symbols string, pattern [12][]rune) error {
	mapping := map[uint16]rune{}
	descr := []rune(symbols)
	var code uint16

	// verify the input is correct
	descrLength := len(descr)
	for i := 0; i < 12; i++ {
		if (descrLength != len(pattern[i])) {
			return errors.New("addEncoding: symbols and pattern lengths mismatch!")
		}
	}

	for col := 0; col < descrLength; col++ {
		code = 0
		for row := uint16(0); row < 12; row++ {
			if (pattern[row][col] == []rune("O")[0]) {
				code |= (1 << row)
			}
		}
		mapping[code] = descr[col]
	}
	encodings[encodingName] = mapping
	return nil
}

func generateZeroTerminatedCArray(a []string) **C.char {
	size := C.size_t((C.size_t(len(a)) + 1) * C.size_t(8)) // XXX YOLO
	res := C.malloc(size)
	r := (*[1 << 30]*C.char)(unsafe.Pointer(res))

	for i := 0; i < len(a); i++ {
		r[i] = C.CString(a[i])
	}
	r[len(a)] = nil

	return (**C.char)(res)
}

func ListEncodings() []string {
	res := make([]string, 0, len(encodings))
	for k := range encodings {
		res = append(res, k)
	}
	sort.Strings(res)

	return res
}

//export ListEncodingsExport
func ListEncodingsExport() **C.char {
	return generateZeroTerminatedCArray(ListEncodings())
}

//export FreeEncodings
func FreeEncodings(a **C.char) {
	r := (*[1 << 30]*C.char)(unsafe.Pointer(a))
	for i := 0; r[i] != nil; i++ {
		C.free(unsafe.Pointer(r[i]))
	}
	C.free(unsafe.Pointer(r))
}

//export DecodeExport
func DecodeExport(encoding *C.char, card *C.int) *C.char {
	bytes := C.GoBytes(unsafe.Pointer(card), 80*4)

	var gcard [80][12]bool
	for i := 0; i < 80; i++ {
		var b1 int
		var b2 int
		var b int
		b1 = int(bytes[i*4])
		b2 = int(bytes[i*4+1])
		b = b1 + b2*(2<<7)
		for j := uint8(0); j < 12; j++ {
			if ((b >> j) & 1) == 1 {
				gcard[i][j] = true
			} else {
				gcard[i][j] = false
			}
		}
	}
	res, err := Decode(C.GoString(encoding), gcard)
	if err != nil {
		return nil
	} else {
		return (*C.char)(C.CString(res))
	}
}

func Decode(encoding string, card [80][12]bool) (string, error) {

	enc, ok := encodings[encoding]
	if !ok {
		return "", errors.New("decode: invalid encoding")
	}

	var res bytes.Buffer
	for i := range card {
		var col uint16 = 0

		for row, x := range card[i] {
			if x {
				col |= (1 << uint16(row))
			}
		}

		if col == 0 {
			res.WriteRune(' ')
			continue
		}

		c, ok := enc[col]
		if !ok {
			return "", errors.New("decode: invalid character")
		}
		res.WriteRune(c)
	}

	return res.String(), nil
}

func checkEncoding(name string, symbols string, pattern [12][]rune) error {
	var testcard [80][12]bool
	for row := 0; row < 12; row++ {
		for col := 0; col < 80 && col < len(pattern[row]); col++ {
			if pattern[row][col] == []rune("O")[0] {
				testcard[col][row] = true
			}
		}
	}

	res, err := Decode(name, testcard)
	if err != nil {
		return err
	}

	if (strings.TrimSpace(res) != strings.TrimSpace(symbols)) {
		return errors.New("checkEncodings: Encoding check failed, pattern and symbols mismatch!")
	}
	return nil
}

func setupEncodings() error {
	const symbols_1401_ibm =
			   "&-0123456789ABCDEFGHIJKLMNOPQR/STUVWXYZ #@:>V?.¤(<§!$*);^±,%='\""
	pattern_1401_ibm := [12][]rune{
		[]rune("O           OOOOOOOOO                        OOOOOO            "),
		[]rune(" O                   OOOOOOOOO                     OOOOOO      "),
		[]rune("  O                           OOOOOOOOO      O     O     OOOOOO"),
		[]rune("   O        O        O        O                                "),
		[]rune("    O        O        O        O       O                 O     "),
		[]rune("     O        O        O        O       O     O     O     O    "),
		[]rune("      O        O        O        O       O     O     O     O   "),
		[]rune("       O        O        O        O       O     O     O     O  "),
		[]rune("        O        O        O        O       O     O     O     O "),
		[]rune("         O        O        O        O       O     O     O     O"),
		[]rune("          O        O        O        O OOOOOO OOOOOOOOOOOOOOOOO"),
		[]rune("           O        O        O        O                        ")}

	err := addEncoding("1401 IBM", symbols_1401_ibm, pattern_1401_ibm)
	if err != nil {
		return err
	}

	err = checkEncoding("1401 IBM", symbols_1401_ibm, pattern_1401_ibm)
	if err != nil {
		return err
	}

	const symbols_029_ibm =
			   "&-0123456789ABCDEFGHIJKLMNOPQR/STUVWXYZb#@'>V?.¤[<§!$*];^±,%v\\¶"
	pattern_029_ibm := [12][]rune{
		[]rune("O           OOOOOOOOO                        OOOOOO            "),
		[]rune(" O                   OOOOOOOOO                     OOOOOO      "),
		[]rune("  O                           OOOOOOOOO                  OOOOOO"),
		[]rune("   O        O        O        O                                "),
		[]rune("    O        O        O        O       O     O     O     O     "),
		[]rune("     O        O        O        O       O     O     O     O    "),
		[]rune("      O        O        O        O       O     O     O     O   "),
		[]rune("       O        O        O        O       O     O     O     O  "),
		[]rune("        O        O        O        O       O     O     O     O "),
		[]rune("         O        O        O        O       O     O     O     O"),
		[]rune("          O        O        O        O OOOOOOOOOOOOOOOOOOOOOOOO"),
		[]rune("           O        O        O        O                        ")}

	err = addEncoding("IBM model 029", symbols_029_ibm, pattern_029_ibm)
	if err != nil {
		return err
	}

	err = checkEncoding("IBM model 029", symbols_029_ibm, pattern_029_ibm)
	if err != nil {
		return err
	}

	const symbols_general_electric =
			   "&-0123456789ABCDEFGHIJKLMNOPQR/STUVWXYZ #@:>V .¤(<§ $*);^±,%='\""
	pattern_general_electric := [12][]rune{
		[]rune("O           OOOOOOOOO                        OOOOOO            "),
		[]rune(" O                   OOOOOOOOO                     OOOOOO      "),
		[]rune("  O                           OOOOOOOOO                  OOOOOO"),
		[]rune("   O        O        O        O                                "),
		[]rune("    O        O        O        O       O     O     O     O     "),
		[]rune("     O        O        O        O       O     O     O     O    "),
		[]rune("      O        O        O        O       O     O     O     O   "),
		[]rune("       O        O        O        O       O     O     O     O  "),
		[]rune("        O        O        O        O       O     O     O     O "),
		[]rune("         O        O        O        O       O     O     O     O"),
		[]rune("          O        O        O        O OOOOOOOOOOOOOOOOOOOOOOOO"),
		[]rune("           O        O        O        O                        ")}

	err = addEncoding("General Electric", symbols_general_electric, pattern_general_electric)
	if err != nil {
		return err
	}

	err = checkEncoding("General Electric", symbols_general_electric, pattern_general_electric)
	if err != nil {
		return err
	}

	return nil
}

//export CheckEncodingExport
func CheckEncodingExport() {
	setupEncodings()
}

func main() {
	// 	err := checkEncoding()
	// 	if err != nil {
	// 		fmt.Println(err)
	// 	}
	//
	// 	fmt.Println(strings.Join(ListEncodings(), ", "))
}
