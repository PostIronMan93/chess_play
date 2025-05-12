// chessboard_piece_move.js

const canvas = document.getElementById('chessboard');
const ctx = canvas.getContext('2d');

const boardSize = 8;
const cellSize = 60;
canvas.width = cellSize * boardSize;
canvas.height = cellSize * boardSize;

let pieces = [];
let selectedPiece = null;
let dragging = false;
let dragPos = null;

const pieceSymbols = {
    white_king: '♔',
    white_queen: '♕',
    white_rook: '♖',
    white_bishop: '♗',
    white_knight: '♘',
    white_pawn: '♙',
    black_king: '♚',
    black_queen: '♛',
    black_rook: '♜',
    black_bishop: '♝',
    black_knight: '♞',
    black_pawn: '♟',
};


// Инициализация фигур
function initPieces() {
    const initial = [
        ['black_rook','black_knight','black_bishop','black_queen','black_king','black_bishop','black_knight','black_rook'],
        ['black_pawn','black_pawn','black_pawn','black_pawn','black_pawn','black_pawn','black_pawn','black_pawn'],
        [null,null,null,null,null,null,null,null],
        [null,null,null,null,null,null,null,null],
        [null,null,null,null,null,null,null,null],
        [null,null,null,null,null,null,null,null],
        ['white_pawn','white_pawn','white_pawn','white_pawn','white_pawn','white_pawn','white_pawn','white_pawn'],
        ['white_rook','white_knight','white_bishop','white_queen','white_king','white_bishop','white_knight','white_rook'],
    ];
    pieces = [];
    for (let y = 0; y < 8; y++) {
        for(let x =0; x<8; x++) {
            const type = initial[y][x];
            if(type) pieces.push({type, x, y, hasMoved: false});
        }
    }
}

//отрисовка доски
function drawBoard() {
    for(let y=0; y<8; y++){
        for(let x=0; x<8; x++) {
            ctx.fillStyle = (x+y) % 2 === 0 ? '#f0d9b5' : '#b58863'; // светлая и темная клетки
            ctx.fillRect(x*cellSize, y*cellSize, cellSize, cellSize);
        }
    }
}

//отрисовка фигур
function drawPieces(){
    ctx.font = `${cellSize - 10}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    for(const piece of pieces){
        if(dragging && piece === selectedPiece) continue; // рисуем перетаскиваемую фигуру отдельно
        const px = piece.x * cellSize + cellSize/2;
        const py = piece.y * cellSize + cellSize/2;
        ctx.fillStyle = piece.type.startsWith('white') ? '#fff' : '#000';
        ctx.fillText(pieceSymbols[piece.type], px, py);
    }
    // Рисуем перетаскиваемую фигуру под мышкой
    if(dragging && selectedPiece && dragPos){
        ctx.fillStyle = selectedPiece.type.startsWith('white') ? '#fff' : '#000';
        ctx.fillText(pieceSymbols[selectedPiece.type], dragPos.x, dragPos.y);
    }
}

function getPieceAt(x, y) {
    return pieces.find(p => p.x === x && p.y === y);
}

// Проверка пути на препятствия, свободен ли путь
function isPathClear(start, end) {
    const dx = Math.sign(end.x - start.x);
    const dy = Math.sign(end.y - start.y);
    let x = start.x + dx;
    let y = start.y + dy;
    while(x !== end.x || y !== end.y){
        if(getPieceAt(x,y)) return false;
        x += dx;
        y += dy;
    }
    return true;
}

// Правила ходов для фигур — с учётом шаха

function canMove(piece, from, to, skipCheck=false) {
    if(to.x < 0 || to.x > 7 || to.y < 0 || to.y > 7) return false;
    if(from.x === to.x && from.y === to.y) return false;

    const target = getPieceAt(to.x, to.y);
    if(target && target.type.split('_')[0] === piece.type.split('_')[0]) return false;

    const dx = to.x - from.x;
    const dy = to.y - from.y;

    // Проверка ходов для каждой фигуры
    switch(piece.type){
        case 'white_pawn': {
            let dir = -1;
            // движение вперёд 1
            if(dx === 0 && dy === dir && !target) return true;
            // движение вперёд на 2 клетки вперёд из начальной позиции
            if(dx === 0 && dy === 2*dir && from.y === 6 && !target && !getPieceAt(from.x, from.y + dir)) return true;
            // взятие по диагонали
            if(Math.abs(dx) === 1 && dy === dir && target && target.type.startsWith('black')) return true;
            return false;
        }
        case 'black_pawn': {
            let dir = 1;
            if(dx === 0 && dy === dir && !target) return true;
            if(dx === 0 && dy === 2*dir && from.y === 1 && !target && !getPieceAt(from.x, from.y + dir)) return true;
            if(Math.abs(dx) === 1 && dy === dir && target && target.type.startsWith('white')) return true;
            return false;
        }
        case 'white_rook':
        case 'black_rook':
            if(dx !== 0 && dy !== 0) return false;
            if(!isPathClear(from, to)) return false;
            return true;
        case 'white_bishop':
        case 'black_bishop':
            if(Math.abs(dx) !== Math.abs(dy)) return false;
            if(!isPathClear(from, to)) return false;
            return true;
        case 'white_queen':
        case 'black_queen':
            if(dx === 0 || dy === 0 || Math.abs(dx) === Math.abs(dy)){
                if(!isPathClear(from, to)) return false;
                return true;
            }
            return false;
        case 'white_king':
        case 'black_king': {
            // Рокировка
            if(!piece.hasMoved && dy === 0 && (dx === 2 || dx === -2)) {
                return canCastle(piece, from, to);
            }
            // стандартный ход 1 клетка
            if(Math.abs(dx) <= 1 && Math.abs(dy) <= 1) return true;
            return false;
        }
        case 'white_knight':
        case 'black_knight':
            if((Math.abs(dx) === 2 && Math.abs(dy) === 1) || (Math.abs(dx) === 1 && Math.abs(dy) === 2)) return true;
            return false;
        default:
            return false;
    }
}

// Проверка шаха для игрока
function isKingInCheck(playerColor) {
    const king = pieces.find(p=>p.type === playerColor + '_king');
    if(!king) return false;
    const enemyColor = playerColor === 'white' ? 'black' : 'white';
    const enemyPieces = pieces.filter(p => p.type.startsWith(enemyColor));
    for(const enemy of enemyPieces){
        if(canMove(enemy, {x: enemy.x, y: enemy.y}, {x: king.x, y: king.y}, true)){
            return true;
        }
    }
    return false;
}

// Сделать ход и проверить , был ли шах до этого хода
function tryMove(piece, from, to) {
    const target = getPieceAt(to.x, to.y);

    // Сохраняем состояние для отката обратно, если после этого хода шах остался
    const backup = {
        pieces: pieces.slice(),
        piecePos: { x: piece.x, y: piece.y },
        captured: target ? target : null,
        hasMoved: piece.hasMoved
    };

    // Сделать ход
    piece.x = to.x;
    piece.y = to.y;
    piece.hasMoved = true;
    if(target){
        pieces = pieces.filter(p => p !== target);
    }

    // Проверять шах после хода
    if(isKingInCheck(piece.type.split('_')[0])){
        // Откатить ход
        piece.x = backup.piecePos.x;

        piece.y = backup.piecePos.y;
        piece.hasMoved = backup.hasMoved;
        if(backup.captured){
            pieces.push(backup.captured);
        }
        return false;
    }
    return true;
}


// Проверка рокировки
function canCastle(king, from, to) {
    if(king.hasMoved) return false;
    if(from.y !== to.y) return false; // рокировка по горизонтали
    const dir = to.x - from.x > 0 ? 1 : -1;

    // Ладья на линии рокировки
    let rookX = dir > 0 ? 7 : 0;
    const rook = getPieceAt(rookX, from.y);
    if(!rook || !rook.type.endsWith('rook') || rook.hasMoved) return false;

    // Проверить есть ли другие фигуры между королём и ладьёй
    for(let x = from.x + dir; x !== rookX; x += dir){
        if(getPieceAt(x, from.y)) return false;
    }

    // Проверить, что король не под шахом, и клетки, через которые он пройдет, тоже не блокируются другиими фигурами по их линии
    const playerColor = king.type.split('_')[0];
    if(isKingInCheck(playerColor)) return false;

    // Проверка клетки после первого шага короля
    let intermediate = { x: from.x + dir, y: from.y };
    // делаем временный ход короля на промежуточную клетку для проверки шаха
    king.x = intermediate.x;
    king.y = intermediate.y;
    const inCheck = isKingInCheck(playerColor);
    king.x = from.x;
    king.y = from.y;
    if(inCheck) return false;

    // рокировка разрешена - все условия выполнены
    return true;
}

// Выполнить рокировку
function doCastle(king, from, to) {
    const dir = to.x - from.x > 0 ? 1 : -1;
    const rookX = dir > 0 ? 7 : 0;
    const rook = getPieceAt(rookX, from.y);

    // Перемещаем короля
    king.x = to.x;
    king.y = to.y;
    king.hasMoved = true;

    // Ладья в центральную клетку рядом с королём
    rook.x = to.x - dir;
    rook.y = to.y;
    rook.hasMoved = true;

    redraw();
}

// Обработка кликов и перетаскивания
canvas.addEventListener('mousedown', e => {
    const rect = canvas.getBoundingClientRect();
    const x = Math.floor((e.clientX - rect.left) / cellSize);
    const y = Math.floor((e.clientY - rect.top) / cellSize);
    const piece = getPieceAt(x, y);
    if(piece){
        selectedPiece = piece;
        dragging = true;
        dragPos = {x: e.clientX - rect.left, y: e.clientY - rect.top};
    }
});

canvas.addEventListener('mousemove', e => {
    if(dragging && selectedPiece){
        const rect = canvas.getBoundingClientRect();
        dragPos = {x: e.clientX - rect.left, y: e.clientY - rect.top};
        redraw();
    }
});

canvas.addEventListener('mouseup', e => {
    if (!dragging) return;
    dragging = false;

    const rect = canvas.getBoundingClientRect();
    const toX = Math.floor((e.clientX - rect.left) / cellSize);
    const toY = Math.floor((e.clientY - rect.top) / cellSize);

    console.log(`Mouse up at: (${toX}, ${toY})`);

    if (selectedPiece) {
        const from = { x: selectedPiece.x, y: selectedPiece.y };
        const to = { x: toX, y: toY };

        console.log(`Trying to move from: (${from.x}, ${from.y}) to: (${to.x}, ${to.y})`);

        // Проверка разрешена ли рокировка
        if (canMove(selectedPiece, from, to)) {
            // Рокировка
            if (selectedPiece.type.endsWith('king') && Math.abs(to.x - from.x) === 2) {
                console.log('Performing castling!');
                doCastle(selectedPiece, from, to);
                sendMove(from.x, from.y, to.x, to.y);
            } else {
                if (tryMove(selectedPiece, from, to)) {
                    console.log('Move successful!');
                    sendMove(from.x, from.y, to.x, to.y);
                } else {
                    alert('Нельзя сделать ход, ваш король под шахом!');
                }
            }
        } else {
            console.warn('Move is not allowed.');
            alert('Недопустимый ход!');
        }
    } else {
        console.warn('No selected piece.');
    }

    selectedPiece = null;
    dragPos = null;
    redraw();
});


function redraw() {
    drawBoard();
    drawPieces();
}

const csrftoken = getCookie('csrftoken');  // Получаем CSRF токен

function sendMove(fromX, fromY, toX, toY) {
    const gameIdInput = document.getElementById('gameId');
    const game_id = gameIdInput ? gameIdInput.value : null;

    if (!game_id) {
    console.warn('game_id не найден');
    return;
    }
    const body = JSON.stringify({
        game_id: game_id,
        old_coords: [fromX, fromY],
        new_coords: [toX, toY]
    });
    console.log('Body being sent:', body);

    fetch('/move_piece/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: body
    })
    .then(response => {
        console.log('Response status:', response.status); // Логи на статус ответа от сервера
        if (!response.ok) {
            throw new Error('HTTP error! Status: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log('Move successful:', data);

    })
    .catch(error => {
        console.error('Ошибка отправки хода:', error);
    });
}



function getCookie(name) {
       let cookieValue = null;
       if (document.cookie && document.cookie !== '') {
           const cookies = document.cookie.split(';');
           for (let i = 0; i < cookies.length; i++) {
               const cookie = cookies[i].trim();
               // Проверяем, начинается ли cookie с имени, которое мы ищем
               if (cookie.substring(0, name.length + 1) === (name + '=')) {
                   cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                   break;
               }
           }
       }
       console.log(`CSRF Token: ${cookieValue}`);
       return cookieValue;
   }


fetch('/new_game/')
  .then(response => response.json())
  .then(data => {
    if(data.status === 'success') {
      console.log('Новая игра создана, game_id:', data.game_id);

    }
  });


initPieces();
redraw();
