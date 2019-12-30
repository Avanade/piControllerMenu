# Copyright (c) 2018 Avanade
# Author: Thor Schueler
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
    The Command class represent a command to be executed by the menu
"""
import subprocess
import logging
from builtin import SysInfo
from display import Display, CONFIRM_OK, CONFIRM_CANCEL

COMMAND_BUILTIN = 0
COMMAND_SHELL = 1

class Command(object):
    """
    Represents a command to be executed
    """

    builtInCommands: dict = {
        "sysInfo": SysInfo
    }

    #region constructor
    def __init__(self, type: int, command: str, processor: str = '', confirm: bool = False):
        """
            Initializes a new instance of the Command class
            Parameters:
                type:       int
                            The type of command. Either COMMAND_BUILTIN or COMMAND_SHELL
                command:    str
                            The actual command to execute. If type is COMMAND_BUILTIN the value must be a valid key inhte 
                            Command.buildInCommands list. If type is COMMAND_SHELL the value must be a command that can be 
                            executed at a shell command prompt
                processor:  str
                            Optional, for future functionality. Not currently used.
                confirm:    bool
                            True to require confirmation before the command is executed, false otherwise. 
        """
        self.__type: int = type
        self.__command: str = command
        self.__processor: str = processor
        self.__returnCode: int = 0
        self.__output: str = ''
        self.__confirm: bool = confirm
        self.__confirmationHandler: callable = None
        self.__spinHandler: callable = None
        self.__outputHandler: callable = None
        self.__running: bool = False
    #endregion

    #region Property defintions
    @property
    def Command(self) -> str:
        """ 
            Gets the command to be executed. If the command type is COMMAND_BUILTIN, this will be the internal 
            key used in Command.builtInCommands. If the command tyoe is COMMAND_SHELL, this will be the shell command
            executed for the command.
        """
        return self.__command

    @property
    def Confirm(self) -> bool:
        """ 
            Gets whether the command required confirmation. If True, a conformation delegate should be set via the 
            ConfirmationHandler property. 
        """
        return self.__confirm

    @property
    def ConfirmationHandler(self) -> callable:
        """ Gets the delegate to be called to confirm command execution. """
        return self.__confirmationHandler

    @ConfirmationHandler.setter
    def ConfirmationHandler(self, handler):
        """ 
            Sets the delegate to be called to confirm command execution. The delegate should be of signature
            (command:Command, state:int = CONFIRM_CANCEL) -> None
        
        """
        self.__confirmationHandler = handler

    @property
    def Output(self) -> str:
        """ Gets the command output (after command completion). """
        return self.__output

    @property
    def OutputHandler(self) -> callable:
        """ Gets the delegate to process the command output for rendering. """
        return self.__outputHandler

    @OutputHandler.setter
    def OutputHandler(self, handler):
        """
            Sets the delegate to process the command output for rendering. The delegate should be of signature
            (command:str, code:int, message:str="") -> None
        """
        self.__outputHandler = handler

    @property
    def SpinHandler(self) -> callable:
        """ Gets the delegate to show a spinner. """
        return self.__spinHandler

    @SpinHandler.setter
    def SpinHandler(self, handler):
        """ 
            Sets the delegate to show a spinner. The delegate should be of signature
            (run=True) -> None
        """
        self.__spinHandler = handler

    @property 
    def Type(self) -> int:
        """ Gets the command type. Either COMMAND_BUILTIN or COMMAND_SHELL. """
        return self.__type
    #endregion

    #region public instance methods
    def Run(self, display: Display, confirmed=CONFIRM_CANCEL):
        """
            Runs the command.
            Parameters:
                display:    Display
                            Reference to a Display instance. This can be NONE if Command.Type is COMMAND_SHELL
                confirmed:  int
                            Optional. Pass CONFIRM_OK to indicate the command has been confirmed. 
        """
        if self.__confirm and self.__confirmationHandler is not None and confirmed==CONFIRM_CANCEL:
            self.__confirmationHandler(self)
        else:
            self.__running = True
            if self.__type == COMMAND_SHELL:
                if self.__spinHandler is not None: self.__spinHandler(True)
                try:
                    self.__output = subprocess.check_output(self.__command, shell=True).decode()
                    self.__returnCode = 0
                except subprocess.CalledProcessError as e:
                    self.__output = e.output.decode()
                    self.__returnCode = e.returncode
                except Exception as e:
                    self.__output = str(e)
                    self.__returnCode = -1000
                if self.__spinHandler is not None: self.__spinHandler(False)
                if self.__outputHandler is not None: self.__outputHandler(self.__command, self.__returnCode, self.__output)
                self.__running = False
            if self.__type == COMMAND_BUILTIN:
                if self.__command in Command.builtInCommands:
                    x = Command.builtInCommands[self.__command](display)
                    x.Run(stop=lambda : display.StopCommand, completed=self.__complete)
    #endregion

    #region public class (static) methods
    @staticmethod
    def FromJSON(data) -> Command:
        """
            Deserialized a command from JSON or YAML. 
            Parameters:
                data:   object
                        Representation of the Command data.
            Returns:
                Instance of Command
        """
        if "type" not in data.keys() or (data["type"] != "shell" and data["type"] != "builtin"):
            message = """Data not in the appropriate format. 
                Expect 'type' attribute to be present and to have a value of either
                'builtin' or 'shell'."""
            logging.exception(message)
            raise Exception(message)
        if "command" not in data.keys() or data["command"] == "":
            message = """Data not in the appropriate format. 
                Expect 'command' attribute to be present and have a value."""
            logging.exception(message)
            raise Exception(message)
        command = Command(
            type=COMMAND_BUILTIN if data["type"] == "builtin" else COMMAND_SHELL,
            command = data["command"],
            processor = data["processor"] if "processor" in data.keys() else None,
            confirm = data["confirm"] if "confirm" in data.keys() else False
          )
        logging.info("Deserialized command {command.Command} successfully")
        return command
    #endregion

    #region private methods
    def __complete(self):
        """
            Delegate to be called from built-in commands to signify command completion. 
        """
        self.__running = False
    #endregion