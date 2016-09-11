function main() {
    fetch('http://localhost:1337/test')
    .then(res => {
        console.log(res.json());
    })
    .catch(err => {
        console.log(`Error: ${err}`);
    });
    document.write('wuddup');
}

main();
