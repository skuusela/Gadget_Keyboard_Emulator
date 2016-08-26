_file = "special_keys"
import working_emulator as emulator
kb_emulator = emulator.KeyboardEmulator(emulator_path="successful_" + _file,
                                                    write_mode="a")
kb_emulator.send_keystrokes_from_file(_file)
