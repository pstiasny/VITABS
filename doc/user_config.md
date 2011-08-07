VITABS user configuration file
==============================

User can override the default setup of VITABS by providing a configuration
(python) script located at `~/.config/vitabs/config.py`.

## Example configuration

    # ed variable contains and instance of the editor
    # ed.st is the text displayed in the status line
    ed.st = "I'm a user configuration file, respect me!"
    
    # load a plugin
    ed.register_handlers(__import__('some_plugin'))
    
    # use a predefined MIDI port number
    # (not guaranteed to work, as this may change when new devices become
    # available!)
    ed.player.change_output(2)
    
    # define own normal-mode mapping
    def my_handler(ed, num):
        ed.st = 'Hello World! Numeric argument: {}'.format(num)
    ed.nmap[ord('!')] = my_handler
    
    # define own command
    def my_command(ed, params):
	    ed.st = 'Hello World! Parameter list: {}'.format(params)
    ed.commands['sayhello'] = my_command
    
    # use an alternative template for displaying a bend
    import vitabs.symbols
    vitabs.symbols.templates['bend'] = '{}^'
