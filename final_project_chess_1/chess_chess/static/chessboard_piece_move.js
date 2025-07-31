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
let currentPlayer = 'white';
let lastDoublePawnMove = null;

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

function switchPlayer() {
    currentPlayer = (currentPlayer === 'white') ? 'black' : 'white';
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

// Проверка валидности lastDoublePawnMove — сбрасываем, если пешки нет
function validateLastDoublePawnMove() {
    if (!lastDoublePawnMove) return;
    const p = getPieceAt(lastDoublePawnMove.x, lastDoublePawnMove.y);
    if (!p || !p.type.endsWith('pawn')) {
        console.log('lastDoublePawnMove сброшен, пешка отсутствует на позиции', lastDoublePawnMove);
        lastDoublePawnMove = null;
    }
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
            // движение вперёд на 1 клетку
            if(dx === 0 && dy === dir && !target) return true;
            // движение вперёд на 2 клетки из начальной позиции
            if(dx === 0 && dy === 2*dir && from.y === 6 && !target && !getPieceAt(from.x, from.y + dir)) return true;
            // взятие по диагонали
            if(Math.abs(dx) === 1 && dy === dir) {
                if(target && target.type.startsWith('black')) return true;

                // Взятие на проходе
                if(lastDoublePawnMove) {
                    const epPawn = getPieceAt(to.x, from.y);
                    if (
                        epPawn &&
                        epPawn.type === 'black_pawn' &&
                        lastDoublePawnMove.x === to.x &&
                        lastDoublePawnMove.y === from.y &&
                        !target
                    ) {
                        return true;
                    }
                }
            }
            return false;
        }
        case 'black_pawn': {
            let dir = 1;
            if(dx === 0 && dy === dir && !target) return true;
            if(dx === 0 && dy === 2*dir && from.y === 1 && !target && !getPieceAt(from.x, from.y + dir)) return true;
            if(Math.abs(dx) === 1 && dy === dir) {
                if(target && target.type.startsWith('white')) return true;

                // Взятие на проходе
                if(lastDoublePawnMove) {
                    const epPawn = getPieceAt(to.x, from.y);
                    if (
                        epPawn &&
                        epPawn.type === 'white_pawn' &&
                        lastDoublePawnMove.x === to.x &&
                        lastDoublePawnMove.y === from.y &&
                        !target
                    ) {
                        return true;
                    }
                }
            }
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
            // стандартный ход на 1 клетку
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
function isKingInCheck(currentPlayer) {
    const king = pieces.find(p=>p.type === currentPlayer + '_king');
    if(!king) return false;
    const enemyColor = currentPlayer === 'white' ? 'black' : 'white';
    const enemyPieces = pieces.filter(p => p.type.startsWith(enemyColor));
    for(const enemy of enemyPieces){
        if(canMove(enemy, {x: enemy.x, y: enemy.y}, {x: king.x, y: king.y}, true)){
            return true;
        }
    }
    return false;
}

function deepClonePieces(pieces) {
    return pieces.map(p => ({ ...p }));
}

// Проверка хода при шахе
function tryMove(piece, from, to) {
    const target = getPieceAt(to.x, to.y);

    // Запрет хода на свою фигуру
    if (target && target.type.split('_')[0] === piece.type.split('_')[0]) {
        console.warn('Нельзя ходить на клетку, занятую своей фигурой');
        return false;
    }

    // Сохраняем копию для отката
    const piecesBackup = deepClonePieces(pieces);

    // Флаг, удалили ли пешку на проходе
    let epPawn = null;

    // Проверка взятия на проходе
    if (
        piece.type.endsWith('pawn') &&
        Math.abs(to.x - from.x) === 1 &&
        to.y - from.y === (piece.type.startsWith('white') ? -1 : 1) &&
        !target
    ) {
        // Проверяем lastDoublePawnMove — координаты пешки, которую можно взять на проходе
        if (
            lastDoublePawnMove &&
            lastDoublePawnMove.x === to.x &&
            lastDoublePawnMove.y === from.y
        ) {
            epPawn = getPieceAt(to.x, from.y);
            if (epPawn && epPawn.type === (piece.type.startsWith('white') ? 'black_pawn' : 'white_pawn')) {
                // Удаляем пешку на проходе
                pieces = pieces.filter(p => p !== epPawn);
            } else {
                // Пешка для взятия отсутствует — ход недопустим
                return false;
            }
        } else {
            // Недопустимый ход
            return false;
        }
    }

    // Выполняем ход
    piece.x = to.x;
    piece.y = to.y;
    piece.hasMoved = true;

    // Рокировка
    if (piece.type.endsWith('king') && Math.abs(to.x - from.x) === 2) {
        const dir = to.x - from.x > 0 ? 1 : -1;
        const rookX = dir > 0 ? 7 : 0;
        const rook = getPieceAt(rookX, from.y);
        if (rook) {
            rook.x = from.x + dir;
            rook.hasMoved = true;
        }
    }

    // Если ход не взятие на проходе и есть target — удаляем фигуру
    if (target && target !== epPawn) {
        pieces = pieces.filter(p => p !== target);
    }

    // Проверка шаха
    if (isKingInCheck(piece.type.split('_')[0])) {
        // Откат
        pieces = piecesBackup;
        return false;
    }

    // Превращение пешки
    if (piece.type.endsWith('pawn')) {
        const lastRank = piece.type.startsWith('white') ? 0 : 7;
        if (piece.y === lastRank) {
            promotePawnWithChoice(piece);
        }
    }

    // Обновляем lastDoublePawnMove для взятия на проходе
    if (piece.type.endsWith('pawn') && Math.abs(to.y - from.y) === 2) {
        lastDoublePawnMove = { x: to.x, y: to.y };
        console.log('lastDoublePawnMove установлен в tryMove:', lastDoublePawnMove);
    } else {
        lastDoublePawnMove = null;
        console.log('lastDoublePawnMove сброшен в tryMove');
    }

    return true;
}


function promotePawnWithChoice(pawn) {
    const color = pawn.type.startsWith('white') ? 'white' : 'black';

    // Варианты фигур для превращения
    const choices = {
        'q': 'queen',
        'r': 'rook',
        'b': 'bishop',
        'n': 'knight'
    };

    let choice = null;
    while (!choice) {
        const input = prompt(
            'Выберите фигуру для превращения пешки:\n' +
            'q - ферзь\n' +
            'r - ладья\n' +
            'b - слон\n' +
            'n - конь\n' +
            '(по умолчанию ферзь, нажмите Cancel)'
        );
        if (input === null) {
            // Отмена - превращаем в ферзя по умолчанию
            choice = 'queen';
        } else {
            const c = input.toLowerCase();
            if (choices[c]) {
                choice = choices[c];
            } else {
                alert('Некорректный выбор. Пожалуйста, введите q, r, b или n.');
            }
        }
    }

    pawn.type = color + '_' + choice;
    return choice;
}

function canRemoveCheck(selectedPiece, from, to) {
    // Создание временного состояния для фигуры
    const originalPosition = { x: selectedPiece.x, y: selectedPiece.y };

    // Перемещение фигуры
    selectedPiece.x = to.x;
    selectedPiece.y = to.y;

    // Проверка, находится ли король под шахом
    const isStillInCheck = isKingInCheck(selectedPiece.type.split('_')[0]);

    // Возвращение фигуры обратно
    selectedPiece.x = originalPosition.x;
    selectedPiece.y = originalPosition.y;

    // Если король под шахом, то фигура возвращается - от шаха не избавились ходом
    return !isStillInCheck;
}

function isCheckmate(currentPlayer) {
    // Проверка, под шахом ли король
    if (!isKingInCheck(currentPlayer)) {
        return false; // Если король не под шахом, то не может быть мата
    }

    const king = pieces.find(p => p.type === currentPlayer + '_king');
    const enemyColor = currentPlayer === 'white' ? 'black' : 'white';
    const allPieces = pieces.filter(p => p.type.startsWith(currentPlayer));

    // Проверка всех возможных ходов всех фигур текущего игрока
    for (const piece of allPieces) {
        for (let x = 0; x < boardSize; x++) {
            for (let y = 0; y < boardSize; y++) {
                const from = { x: piece.x, y: piece.y };
                const to = { x: x, y: y };
                if (canMove(piece, from, to)) {
                    // Временное перемещение фигуры
                    const originalPosition = { x: piece.x, y: piece.y };
                    piece.x = to.x;
                    piece.y = to.y;

                    // Проверка находится ли ещё король под шахом
                    const stillInCheck = isKingInCheck(currentPlayer);

                    // Возврат фигуры обратно
                    piece.x = originalPosition.x;
                    piece.y = originalPosition.y;

                    // Если есть хоть один ход, который избавляет от шаха, возвращаем false
                    if (!stillInCheck) {
                        return false; // У игрока есть возможный ход
                    }
                }
            }
        }
    }

    // Если ни один из ходов не возможен и король под шахом, то это мат
    return true;
}

function isStalemate(currentPlayer) {
    if (isKingInCheck(currentPlayer)) {
        return false; // Если король под шахом — это не пат
    }

    const allPieces = pieces.filter(p => p.type.startsWith(currentPlayer));

    for (const piece of allPieces) {
        for (let x = 0; x < boardSize; x++) {
            for (let y = 0; y < boardSize; y++) {
                const from = { x: piece.x, y: piece.y };
                const to = { x: x, y: y };

                if (canMove(piece, from, to)) {
                    // Выполняем временный ход
                    const originalPosition = { x: piece.x, y: piece.y };
                    const targetPiece = getPieceAt(to.x, to.y);

                    piece.x = to.x;
                    piece.y = to.y;

                    // Убираем взятую фигуру временно, если есть
                    if (targetPiece) {
                        pieces = pieces.filter(p => p !== targetPiece);
                    }

                    const stillInCheck = isKingInCheck(currentPlayer);

                    // Откатываем ход
                    piece.x = originalPosition.x;
                    piece.y = originalPosition.y;

                    if (targetPiece) {
                        pieces.push(targetPiece);
                    }

                    if (!stillInCheck) {
                        return false; // Есть хотя бы один легальный ход
                    }
                }
            }
        }
    }

    // Ни одного легального хода нет и король не под шахом — пат
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

    // Есть ли другие фигуры между королём и ладьёй
    for(let x = from.x + dir; x !== rookX; x += dir){
        if(getPieceAt(x, from.y)) return false;
    }

    const currentPlayer = king.type.split('_')[0];

    // Проверка, что король не под шахом в начальной позиции
    if(isKingInCheck(currentPlayer)) return false;

    // Проверка клетки после первого шага короля (промежуточная клетка)
    let intermediate = { x: from.x + dir, y: from.y };
    king.x = intermediate.x;
    king.y = intermediate.y;
    if(isKingInCheck(currentPlayer)) {
        king.x = from.x;
        king.y = from.y;
        return false;
    }

    // Проверка конечной клетки короля (куда он перемещается при рокировке)
    king.x = to.x;
    king.y = to.y;
    if(isKingInCheck(currentPlayer)) {
        king.x = from.x;
        king.y = from.y;
        return false;
    }

    // Восстанавливаем позицию короля
    king.x = from.x;
    king.y = from.y;

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

    if (!selectedPiece) {
        redraw();
        return;
    }

    const from = { x: selectedPiece.x, y: selectedPiece.y };
    const to = { x: toX, y: toY };
    const pieceColor = selectedPiece.type.split('_')[0];
    const dx = to.x - from.x;
    const dy = to.y - from.y;

    if (currentPlayer !== pieceColor) {
        alert('Нельзя ходить за чужую фигуру!');
        redraw();
        selectedPiece = null;
        return;
    }

    const targetPiece = getPieceAt(to.x, to.y);
    if (targetPiece && targetPiece.type.split('_')[0] === currentPlayer) {
        alert('Нельзя ходить на клетку, занятую своей фигурой!');
        redraw();
        selectedPiece = null;
        return;
    }

    if (!canMove(selectedPiece, from, to)) {
        alert('Недопустимый ход!');
        redraw();
        selectedPiece = null;
        return;
    }

    console.log('Попытка хода с', from, 'на', to);
    console.log('lastDoublePawnMove перед ходом:', lastDoublePawnMove);

    // Рокировка
    if (selectedPiece.type.endsWith('king') && !selectedPiece.hasMoved && dy === 0 && (dx === 2 || dx === -2)) {
        if (canCastle(selectedPiece, from, to)) {
            sendMove(from.x, from.y, to.x, to.y, true);
            selectedPiece.hasMoved = true;
            switchPlayer();
            selectedPiece = null;
            redraw();
            return;
        } else {
            alert('Рокировка невозможна!');
            redraw();
            selectedPiece = null;
            return;
        }
    }

    // Взятие на проходе — не удаляем пешку здесь, это делает tryMove

    // Попытка сделать ход
    const moveAllowed = tryMove(selectedPiece, from, to);

    if (!moveAllowed) {
        alert('Этот ход оставит Вас под шахом, либо невозможен!');
        redraw();
        selectedPiece = null;
        return;
    }

    // Обновление lastDoublePawnMove уже сделано в tryMove

    sendMove(from.x, from.y, to.x, to.y, false);

    switchPlayer();

    if (isKingInCheck(currentPlayer)) {
        alert('Ваш король под шахом!');
    }

    if (isCheckmate(currentPlayer)) {
        alert('Мат! Игра окончена.');
    } else if (isStalemate(currentPlayer)) {
        alert('Пат! Игра окончена.');
    }

    selectedPiece = null;
    redraw();
});



function redraw() {
    drawBoard();
    drawPieces();
}

const csrftoken = getCookie('csrftoken');  // Получаем CSRF токен

function sendMove(fromX, fromY, toX, toY, castle = false, promotion = null) {
    const gameIdInput = document.getElementById('gameId');
    const game_id = gameIdInput ? gameIdInput.value : null;

    if (!game_id) {
        console.warn('game_id не найден');
        return;
    }

    const bodyObj = {
        game_id: game_id,
        old_coords: [fromX, fromY],
        new_coords: [toX, toY],
        castle: castle
    };

    if (promotion) {
        bodyObj.promotion = promotion;  // Добавляем параметр превращения
    }

    const body = JSON.stringify(bodyObj);

    console.log('Body being sent:', body);

    fetch('/move_piece/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: body
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);

        if (data.status === "success") {
            if (castle) {
                if (data.boardState) {
                    updateBoard(data.boardState);
                }
            } else {
                const piece = getPieceAt(fromX, fromY);
                if (piece) {
                    piece.x = toX;
                    piece.y = toY;
                    piece.hasMoved = true;

                    // Обновляем тип фигуры, если было превращение
                    if (promotion) {
                        const color = piece.type.split('_')[0];
                        piece.type = color + '_' + promotion;
                    }
                }
            }

            currentPlayer = data.next_turn;

            // Обновляем lastDoublePawnMove из ответа сервера
            lastDoublePawnMove = data.lastDoublePawnMove || null;
            validateLastDoublePawnMove();

            redraw();

            console.log('Ход выполнен успешно');
        } else {
            console.warn('Ошибка:', data.message);
        }
    })
    .catch(error => {
        console.error('Ошибка:', error.message);
    });
}


function updateBoard(boardState) {
    pieces = [];
    const typeMap = {
        k: 'king',
        q: 'queen',
        r: 'rook',
        b: 'bishop',
        n: 'knight',
        p: 'pawn'
    };

    for (let y = 0; y < 8; y++) {
        for (let x = 0; x < 8; x++) {
            const cell = boardState[y][x];
            if (cell !== null) {
                pieces.push({
                    type: cell.color + '_' + typeMap[cell.type.toLowerCase()],
                    x: x,
                    y: y,
                    hasMoved: cell.hasMoved || false
                });
            }
        }
    }
    validateLastDoublePawnMove();
    drawBoard();
    drawPieces();
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


document.addEventListener('DOMContentLoaded', () => {
    const gameIdInput = document.getElementById('gameId');
    let gameId = gameIdInput.value;

    if (!gameId) {
        document.getElementById('newGameBtn').addEventListener('click', () => {
            fetch('/new_game/', {
                method: 'POST'
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.json();
                }
            })
            .then(data => {
                if (data && data.game_id) {
                    gameId = data.game_id;
                    gameIdInput.value = gameId;
                    loadBoardFromServer(gameId);
                }
            })
            .catch(error => {
                console.error('Ошибка при создании новой игры:', error);
            });
        });
    } else {
        loadBoardFromServer(gameId);
    }
});

// Функция загрузки состояния доски
function loadBoardFromServer(gameId) {
    console.log('loadBoardFromServer с gameId:', gameId);
    fetch(`/get_board_state/?game_id=${gameId}`)
        .then(response => {
            if(!response.ok) throw new Error('HTTP ' + response.status);
            return response.json();
        })
        .then(data => {
            console.log('Ответ сервера:', data);
            if(data && data.pieces) {
                pieces = data.pieces.map(p => ({
                    type: p.type,
                    x: p.x,
                    y: p.y,
                    hasMoved: p.hasMoved || false
                }));
            } else if(data && data.boardState) {
                pieces = [];
                const typeMap = {k:'king',q:'queen',r:'rook',b:'bishop',n:'knight',p:'pawn'};
                for(let y=0; y<8; y++) {
                    for(let x=0; x<8; x++) {
                        const cell = data.boardState[y][x];
                        if(cell !== null) {
                            pieces.push({
                                type: cell.color + '_' + typeMap[cell.type.toLowerCase()],
                                x, y,
                                hasMoved: cell.hasMoved || false
                            });
                        }
                    }
                }
            } else {
                initPieces();
            }

            // Обновляем текущего игрока
            if (data && data.currentTurn) {
                currentPlayer = data.currentTurn; // 'white' или 'black'
            } else {
                currentPlayer = 'white'; // по умолчанию
            }

            redraw();
        })
        .catch(err => {
            console.error('Ошибка загрузки состояния доски:', err);
            initPieces();
            currentPlayer = 'white';
            redraw();
        });
}
