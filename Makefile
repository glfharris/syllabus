build: clean buildui
	mkdir -p build/dist21
	cp syllabus/* build/dist21

clean:
	rm -rf build/*

buildui: cleanui
	pyuic5 ui/ui_dialog.ui -o syllabus/ui_dialog.py

cleanui:
	rm -f syllabus/ui_dialog.py

testinstall: build testclean
	cp -r build/dist21 ~/.local/share/Anki2/addons21/syllabus-test

testclean:
	rm -rf ~/.local/share/Anki2/addons21/syllabus-test

test: testinstall
	anki
