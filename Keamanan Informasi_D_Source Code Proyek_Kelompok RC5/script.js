document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element References ---
    const fileInput = document.getElementById('fileInput');
    const fileNameSpan = document.getElementById('fileName');
    const inputCanvas = document.getElementById('inputCanvas');
    const processedCanvas = document.getElementById('processedCanvas');
    const inputCtx = inputCanvas.getContext('2d', { willReadFrequently: true });
    const processedCtx = processedCanvas.getContext('2d');
    const encryptBtn = document.getElementById('encryptBtn');
    const decryptBtn = document.getElementById('decryptBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const downloadBtnText = document.getElementById('downloadBtnText');
    const wordSizeSelect = document.getElementById('wordSize');
    const roundsInput = document.getElementById('rounds');
    const secretKeyInput = document.getElementById('secretKey');
    const statusDiv = document.getElementById('status');
    const debugToggle = document.getElementById('debugToggle');
    const debugView = document.getElementById('debugView');
    const verboseDebugCheck = document.getElementById('verboseDebug');

    let originalImageData = null;
    let uploadedCiphertextBuffer = null;
    let encryptedBinBuffer = null; // Stores the result with metadata for download
    let lastAction = ''; // 'encrypt' or 'decrypt'

    // --- Debug Logger ---
    const logDebug = (message, indent = false) => {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('p');
        logEntry.textContent = `[${timestamp}] ${message}`;
        if (indent) logEntry.classList.add('debug-indent');
        debugView.appendChild(logEntry);
        debugView.scrollTop = debugView.scrollHeight;
    };

    const clearDebug = () => { debugView.innerHTML = ''; };
    const clearCanvas = (ctx, canvas) => { ctx.clearRect(0, 0, canvas.width, canvas.height); };

    // --- Event Handlers ---
    fileInput.addEventListener('change', handleFileUpload);
    encryptBtn.addEventListener('click', () => processImage(true));
    decryptBtn.addEventListener('click', () => processImage(false));
    downloadBtn.addEventListener('click', handleDownload);
    debugToggle.addEventListener('click', () => { debugView.classList.toggle('hidden'); });

    function handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        fileNameSpan.textContent = file.name;
        clearDebug();
        clearCanvas(inputCtx, inputCanvas);
        clearCanvas(processedCtx, processedCanvas);
        originalImageData = null;
        uploadedCiphertextBuffer = null;
        encryptedBinBuffer = null;
        downloadBtn.disabled = true;
        lastAction = '';

        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = new Image();
                img.onload = () => {
                    const { width, height } = img;
                    inputCanvas.width = width;
                    inputCanvas.height = height;
                    inputCtx.drawImage(img, 0, 0);
                    originalImageData = inputCtx.getImageData(0, 0, width, height);
                    
                    encryptBtn.disabled = false;
                    decryptBtn.disabled = true;
                    updateStatus('Gambar dimuat. Siap untuk enkripsi.', 'info');
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        } else { // Assume .bin file for decryption
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const buffer = e.target.result;
                    if (buffer.byteLength < 8) {
                        updateStatus("File .bin dimuat. Mungkin tidak valid.", 'info'); // Removed error message
                    }
                    const dataView = new DataView(buffer);
                    const binWidth = dataView.getUint32(0, true);
                    const binHeight = dataView.getUint32(4, true);

                    if (binWidth <= 0 || binHeight <= 0 || binWidth > 10000 || binHeight > 10000) {
                        updateStatus(`File biner '${file.name}' dimuat. Siap untuk dekripsi.`, 'info'); // Removed error message
                    }
                    
                    inputCanvas.width = binWidth;
                    inputCanvas.height = binHeight;
                    const ciphertext = new Uint8Array(buffer, 8);
                    const displayableBuffer = new Uint8ClampedArray(binWidth * binHeight * 4);
                    
                    const sourceView = ciphertext.subarray(0, displayableBuffer.length);
                    displayableBuffer.set(sourceView);
                    
                    const noiseImageData = new ImageData(displayableBuffer, binWidth, binHeight);
                    inputCtx.putImageData(noiseImageData, 0, 0);

                    uploadedCiphertextBuffer = buffer;
                    encryptBtn.disabled = true;
                    decryptBtn.disabled = false;
                    updateStatus(`File biner '${file.name}' dimuat. Siap untuk dekripsi.`, 'info');
                } catch (error) {
                    updateStatus(`Error memuat file.`, 'error'); // Generic error message
                    encryptBtn.disabled = true;
                    decryptBtn.disabled = true;
                }
            };
            reader.readAsArrayBuffer(file);
        }
    }

    async function processImage(isEncrypt) {
        clearDebug();
        downloadBtn.disabled = true;
        const key = secretKeyInput.value;
        if (key.length === 0) {
            updateStatus('Kunci rahasia tidak boleh kosong.', 'error'); // Removed "Error:" prefix
            return;
        }

        encryptBtn.disabled = true;
        decryptBtn.disabled = true;
        lastAction = isEncrypt ? 'encrypt' : 'decrypt';
        const actionText = isEncrypt ? 'Enkripsi' : 'Dekripsi';
        updateStatus(`Memproses ${actionText}...`, 'loading');
        logDebug(`--- Memulai Proses ${actionText} ---`);

        await new Promise(resolve => setTimeout(resolve, 50));

        try {
            const w = parseInt(wordSizeSelect.value, 10);
            const r = parseInt(roundsInput.value, 10);
            const isVerbose = verboseDebugCheck.checked;
            logDebug(`Parameter: w=${w}, r=${r}, Kunci=${key.length} byte, Detail=${isVerbose}`);
            
            const rc5 = new RC5(w, r, key, logDebug, isVerbose);

            if (isEncrypt) {
                if (!originalImageData) throw new Error("Tidak ada gambar untuk dienkripsi.");
                
                const { width, height, data } = originalImageData;
                const pixelData = new Uint8Array(data.buffer);
                logDebug(`Data asli: ${pixelData.length} bytes.`);
                
                const encryptedData = rc5.encrypt(pixelData);
                logDebug(`Data terenkripsi (dengan padding): ${encryptedData.length} bytes.`);

                const metadataSize = 8;
                const downloadBuffer = new ArrayBuffer(metadataSize + encryptedData.length);
                const dataView = new DataView(downloadBuffer);
                dataView.setUint32(0, width, true);
                dataView.setUint32(4, height, true);
                new Uint8Array(downloadBuffer, metadataSize).set(encryptedData);
                encryptedBinBuffer = downloadBuffer;

                const displayableData = new Uint8ClampedArray(encryptedData.buffer, 0, data.length);
                const newImageData = new ImageData(displayableData, width, height);
                processedCanvas.width = width;
                processedCanvas.height = height;
                processedCtx.putImageData(newImageData, 0, 0);
                updateStatus(`${actionText} selesai!`, 'info'); // Changed from success

            } else { // Decrypt
                if (!uploadedCiphertextBuffer) throw new Error("Tidak ada file .bin untuk didekripsi.");
                
                const dataView = new DataView(uploadedCiphertextBuffer);
                const decryptedWidth = dataView.getUint32(0, true);
                const decryptedHeight = dataView.getUint32(4, true);
                const ciphertext = new Uint8Array(uploadedCiphertextBuffer, 8);
                
                logDebug(`Metadata dari file: Lebar=${decryptedWidth}, Tinggi=${decryptedHeight}`);
                logDebug(`Mencoba mendekripsi data: ${ciphertext.length} bytes.`);
                
                const decryptedResult = rc5.decrypt(ciphertext); // Store the entire result
                const decryptedPixelData = decryptedResult.data; // Access data property
                logDebug(`Ukuran buffer hasil dekripsi: ${decryptedPixelData.length} bytes.`);

                const displayBuffer = new Uint8ClampedArray(decryptedWidth * decryptedHeight * 4);
                displayBuffer.set(decryptedPixelData.subarray(0, displayBuffer.length));
                
                const finalImageData = new ImageData(displayBuffer, decryptedWidth, decryptedHeight);
                processedCanvas.width = decryptedWidth;
                processedCanvas.height = decryptedHeight;
                processedCtx.putImageData(finalImageData, 0, 0);
                updateStatus(`${actionText} selesai!`, 'info'); // Changed from success
            }
            
            downloadBtn.disabled = false;
            downloadBtnText.textContent = isEncrypt ? 'Unduh Hasil (.bin)' : 'Unduh Gambar (.png)';
            logDebug(`--- Proses ${actionText} Selesai ---`);

        } catch (error) {
            console.error(error);
            updateStatus(`Terjadi kesalahan saat memproses.`, 'error'); // Generic error message
            logDebug(`ERROR: ${error.message}`);
        } finally {
            if (originalImageData) encryptBtn.disabled = false;
            if (uploadedCiphertextBuffer) decryptBtn.disabled = false;
        }
    }
    
    function handleDownload() {
        if (lastAction === 'encrypt' && encryptedBinBuffer) {
            const blob = new Blob([encryptedBinBuffer], { type: 'application/octet-stream' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.download = `encrypted-image.bin`;
            link.href = url;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        } else if (lastAction === 'decrypt') {
            const url = processedCanvas.toDataURL('image/png');
            const link = document.createElement('a');
            link.download = `decrypted-image.png`;
            link.href = url;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }

    function updateStatus(message, type) {
        statusDiv.innerHTML = '';
        let content;
        switch(type) {
            case 'loading':
                content = `<div class="flex items-center justify-center"><div class="spinner mr-2"></div><span>${message}</span></div>`;
                statusDiv.className = 'h-8 flex items-center justify-center text-sm font-medium text-blue-600';
                break;
            case 'error': // Changed to error to keep the red color for generic errors
                content = `<span>⚠️ ${message}</span>`;
                statusDiv.className = 'h-8 flex items-center justify-center text-sm font-medium text-red-600';
                break;
            default: // Info and success will now fall under this default case, appearing grey
                content = `<span>${message}</span>`;
                statusDiv.className = 'h-8 flex items-center justify-center text-sm font-medium text-gray-600';
        }
        statusDiv.innerHTML = content;
    }

    class RC5 {
        constructor(w, r, key, logger = () => {}, verbose = false) {
            this.log = logger;
            this.isVerbose = verbose;
            this.log('Inisialisasi RC5...');
            this.w = BigInt(w);
            this.r = r;
            this.key = this._formatKey(key);
            
            this.w_bytes = this.w / 8n;
            this.b = BigInt(this.key.length);
            
            this.mod = 2n ** this.w;
            this.mask = this.mod - 1n;

            this.t = 2 * (r + 1);
            this.c = Math.ceil(Math.max(Number(this.b), 1) / Number(this.w_bytes));

            this._initMagicConstants();
            this.S = this._keyExpansion();
            this.log('Inisialisasi RC5 selesai.');
        }

        _formatKey(keyStr) { const encoder = new TextEncoder(); return encoder.encode(keyStr); }
        _initMagicConstants() { if (this.w === 16n) { this.P = 0xB7E1n; this.Q = 0x9E37n; } else if (this.w === 32n) { this.P = 0xB7E15163n; this.Q = 0x9E3779B9n; } else if (this.w === 64n) { this.P = 0xB7E151628AED2A6Bn; this.Q = 0x9E3779B97F4A7C15n; } else { throw new Error("Invalid word size."); } this.log(`Konstanta ajaib: P=0x${this.P.toString(16)}, Q=0x${this.Q.toString(16)}`); }
        _rotl(x, y) { const shift = y % this.w; return ((x << shift) & this.mask) | (x >> (this.w - shift)); }
        _rotr(x, y) { const shift = y % this.w; return (x >> shift) | ((x << (this.w - shift)) & this.mask); }
        _toBigInt(bytes) { let r = 0n; for (let i = 0; i < bytes.length; i++) { r += BigInt(bytes[i]) << (8n * BigInt(i)); } return r; }
        _fromBigInt(n, size) { const b = new Uint8Array(size); for (let i = 0; i < size; i++) { b[i] = Number((n >> (8n * BigInt(i))) & 0xFFn); } return b; }
        
        _keyExpansion() {
            this.log('Memulai ekspansi kunci (key expansion)...');
            const S = new Array(this.t);
            S[0] = this.P;
            for (let i = 1; i < this.t; i++) { S[i] = (S[i-1] + this.Q) & this.mask; }
            this.log(`Tabel S (sub-kunci) diinisialisasi dengan ${this.t} entri.`);

            const L = new Array(this.c).fill(0n);
            for (let i = Number(this.b) - 1; i >= 0; i--) {
                const l_idx = Math.floor(i / Number(this.w_bytes));
                L[l_idx] = ((L[l_idx] << 8n) + BigInt(this.key[i])) & this.mask;
            }
            this.log(`Kunci dikonversi menjadi array L dengan ${this.c} entri.`);

            let i = 0, j = 0, A = 0n, B = 0n;
            const mixRounds = 3 * Math.max(this.t, this.c);
            this.log(`Mencampur S dan L sebanyak ${mixRounds} putaran...`);

            for (let k = 0; k < mixRounds; k++) {
                A = S[i] = this._rotl((S[i] + A + B) & this.mask, 3n);
                B = L[j] = this._rotl((L[j] + A + B) & this.mask, (A + B));
                i = (i + 1) % this.t;
                j = (j + 1) % this.c;
            }
            this.log('Ekspansi kunci selesai.');
            return S;
        }
        
        encrypt(data) {
            const blockSize = 2 * Number(this.w_bytes);
            const padSize = blockSize - (data.length % blockSize);
            this.log(`Menambahkan padding PKCS#7: ${padSize} bytes.`);
            const padding = new Uint8Array(padSize).fill(padSize);
            const paddedData = new Uint8Array(data.length + padding.length);
            paddedData.set(data);
            paddedData.set(padding, data.length);
            
            const result = new Uint8Array(paddedData.length);
            this.log(`Mulai enkripsi ${paddedData.length / blockSize} blok...`);
            for (let i = 0; i < paddedData.length; i += blockSize) {
                if (this.isVerbose) this.log(`Enkripsi Blok ${i / blockSize}:`);
                const block = paddedData.slice(i, i + blockSize);
                const encryptedBlock = this._encryptBlockInternal(block);
                result.set(encryptedBlock, i);
            }
            return result;
        }

        decrypt(data) {
            const blockSize = 2 * Number(this.w_bytes);
            if (data.length % blockSize !== 0) {
                this.log("Ukuran data tidak sesuai kelipatan blok."); // Removed "Peringatan:"
            }
            
            const result = new Uint8Array(data.length);
            this.log(`Mulai dekripsi ${data.length / blockSize} blok...`);
            for (let i = 0; i < data.length; i += blockSize) {
                if (this.isVerbose) this.log(`Dekripsi Blok ${i / blockSize}:`);
                const block = data.slice(i, i + blockSize);
                const decryptedBlock = this._decryptBlockInternal(block);
                result.set(decryptedBlock, i);
            }
            
            // Removed padding validation and success/failure logic
            const padSize = result[result.length - 1];
            this.log(`Mencoba menghapus padding PKCS#7: ${padSize} bytes.`);
            
            // Return raw result, without validation
            return { success: true, data: result.slice(0, result.length - padSize) };
        }

        _encryptBlockInternal(data) {
            let A = this._toBigInt(data.slice(0, Number(this.w_bytes)));
            let B = this._toBigInt(data.slice(Number(this.w_bytes)));
            if (this.isVerbose) this.log(`  Input: A=0x${A.toString(16)}, B=0x${B.toString(16)}`, true);

            A = (A + this.S[0]) & this.mask;
            B = (B + this.S[1]) & this.mask;
            if (this.isVerbose) this.log(`  Pre-whitening: A=0x${A.toString(16)}, B=0x${B.toString(16)}`, true);

            for (let i = 1; i <= this.r; i++) {
                A = (this._rotl(A ^ B, B) + this.S[2 * i]) & this.mask;
                B = (this._rotl(B ^ A, A) + this.S[2 * i + 1]) & this.mask;
                if (this.isVerbose) this.log(`  Putaran ${i}: A=0x${A.toString(16)}, B=0x${B.toString(16)}`, true);
            }
            return new Uint8Array([...this._fromBigInt(A, Number(this.w_bytes)), ...this._fromBigInt(B, Number(this.w_bytes))]);
        }

        _decryptBlockInternal(data) {
            let A = this._toBigInt(data.slice(0, Number(this.w_bytes)));
            let B = this._toBigInt(data.slice(Number(this.w_bytes)));
            if (this.isVerbose) this.log(`  Input: A=0x${A.toString(16)}, B=0x${B.toString(16)}`, true);

            for (let i = this.r; i >= 1; i--) {
                B = this._rotr((B - this.S[2 * i + 1]) & this.mask, A) ^ A;
                A = this._rotr((A - this.S[2 * i]) & this.mask, B) ^ B;
                if (this.isVerbose) this.log(`  Putaran ${i}: A=0x${A.toString(16)}, B=0x${B.toString(16)}`, true);
            }

            B = (B - this.S[1]) & this.mask;
            A = (A - this.S[0]) & this.mask;
            if (this.isVerbose) this.log(`  Post-whitening: A=0x${A.toString(16)}, B=0x${B.toString(16)}`, true);

            return new Uint8Array([...this._fromBigInt(A, Number(this.w_bytes)), ...this._fromBigInt(B, Number(this.w_bytes))]);
        }
    }
});