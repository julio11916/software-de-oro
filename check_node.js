const fs = require('fs');
const path = require('path');
const dir = 'static/img/estampados/ejercito/pañoleta/Escudos';
const files = fs.readdirSync(dir);
console.log(files);
