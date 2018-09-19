build: clean buildui
	mkdir -p build/dist21
	cp -r syllabus/* build/dist21

clean:
	rm -rf build/*

buildrelease: build
	cd build/dist21; zip -r ../anki-syllabus-v21.zip .

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
