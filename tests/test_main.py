import sys
sys.path.append('/home/ubuntu/workspace/hello_world_demo')


import pytest
#from hello_world.main import main
from hello_world import main

def test_main(capsys):
    main()
    captured = capsys.readouterr()
    assert captured.out == "Hello, World!\n"
