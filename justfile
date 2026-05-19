addon_dir := `echo ~/.local/share/Anki2/addons21/syllabus-test`
package := "anki-syllabus-v21"

build:
    rm -rf syllabus/__pycache__
    mkdir -p ./build
    rm -f ./build/{{ package }}.ankiaddon
    cd syllabus && zip -r ../build/{{ package }}.ankiaddon . -x "*__pycache__*"

clean:
    rm -rf ./build

test: testclean
    cp -r ./syllabus {{ addon_dir }}
    find {{ addon_dir }} -name __pycache__ -type d -prune -exec rm -rf {} +
    anki

testclean:
    rm -rf {{ addon_dir }}
