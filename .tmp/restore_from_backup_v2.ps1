$ErrorActionPreference = "Stop"
$backup = "db\software_de_oro_backup_2026-03-07.sql"
$lines = Get-Content $backup

function Get-CopyRows([string]$table) {
    $pattern = "^COPY public\.$table \(.*\) FROM stdin;$"
    $startIdx = -1
    for ($i=0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match $pattern) { $startIdx = $i; break }
    }
    if ($startIdx -lt 0) { return @() }

    $rows = New-Object System.Collections.Generic.List[string]
    for ($j=$startIdx+1; $j -lt $lines.Count; $j++) {
        $line = $lines[$j]
        if ($line.Trim() -eq "\\.") { break }
        $rows.Add($line)
    }
    return $rows
}

function Write-RowsFile([string]$path, $rows) {
    [System.IO.File]::WriteAllLines($path, $rows, [System.Text.UTF8Encoding]::new($false))
}

function Run-Psql([string]$sql) {
    & $psql @dbArgs -c $sql
    if ($LASTEXITCODE -ne 0) { throw "psql fallo: $sql" }
}

function Copy-FromFile([string]$file, [string]$copySql) {
    Get-Content $file | & $psql @dbArgs -c $copySql
    if ($LASTEXITCODE -ne 0) { throw "COPY fallo: $file" }
}

New-Item -ItemType Directory -Force -Path .tmp | Out-Null

$u = Get-CopyRows "usuarios"
$r = Get-CopyRows "registros"
$c = Get-CopyRows "categoria_producto"
$pr = Get-CopyRows "producto"
$pe = Get-CopyRows "pedidos"
$d = Get-CopyRows "detalle_pedido"
$pm = Get-CopyRows "promociones"
$pa = Get-CopyRows "pagos"

$pr8 = New-Object System.Collections.Generic.List[string]
foreach ($row in $pr) {
    if ([string]::IsNullOrWhiteSpace($row)) { continue }
    $parts = $row -split "`t"
    if ($parts.Length -lt 8) { continue }
    $pr8.Add(($parts[0..7] -join "`t"))
}

$uFile = ".tmp\usuarios.tsv"
$rFile = ".tmp\registros.tsv"
$cFile = ".tmp\categoria_producto.tsv"
$prFile = ".tmp\producto.tsv"
$peFile = ".tmp\pedidos.tsv"
$dFile = ".tmp\detalle_pedido.tsv"
$pmFile = ".tmp\promociones.tsv"
$paFile = ".tmp\pagos.tsv"

Write-RowsFile $uFile $u
Write-RowsFile $rFile $r
Write-RowsFile $cFile $c
Write-RowsFile $prFile $pr8
Write-RowsFile $peFile $pe
Write-RowsFile $dFile $d
Write-RowsFile $pmFile $pm
Write-RowsFile $paFile $pa

$env:PGPASSWORD='admin'
$psql = "C:\Program Files\PostgreSQL\18\bin\psql.exe"
$dbArgs = @('-h','localhost','-p','5432','-U','postgres','-d','software_de_oro','-v','ON_ERROR_STOP=1')

Run-Psql "TRUNCATE TABLE detalle_pedido, pagos, pedidos, producto, promociones, registros, categoria_producto, usuarios RESTART IDENTITY CASCADE;"
Copy-FromFile $uFile  "COPY usuarios (id_usuario, nombre, email, password_hash, rol, estado, fecha_registro, email_verified, verification_code, verification_code_expiry) FROM STDIN;"
Copy-FromFile $rFile  "COPY registros (id_registro, id_usuario, accion, fecha_accion) FROM STDIN;"
Copy-FromFile $cFile  "COPY categoria_producto (id_categoria, nombre_categoria, descripcion) FROM STDIN;"
Copy-FromFile $prFile "COPY producto (id_producto, nombre, descripcion, precio, stock, id_categoria, imagen_url, eliminado) FROM STDIN;"
Copy-FromFile $peFile "COPY pedidos (id_pedido, id_usuario, fecha_pedido, estado) FROM STDIN;"
Copy-FromFile $dFile  "COPY detalle_pedido (id_detalle, id_pedido, id_producto, cantidad, subtotal) FROM STDIN;"
Copy-FromFile $pmFile "COPY promociones (id_promo, nombre, descripcion, tipo_descuento, valor_descuento, codigo, fecha_inicio, fecha_fin, activo) FROM STDIN;"
Copy-FromFile $paFile "COPY pagos (id_pago, id_pedido, monto, metodo_pago, fecha_pago, estado_pago, id_promo, codigo_promo, tipo_descuento, valor_descuento, monto_descuento) FROM STDIN;"

Run-Psql "SELECT setval(pg_get_serial_sequence('usuarios','id_usuario'), COALESCE((SELECT MAX(id_usuario) FROM usuarios),1), true);"
Run-Psql "SELECT setval(pg_get_serial_sequence('categoria_producto','id_categoria'), COALESCE((SELECT MAX(id_categoria) FROM categoria_producto),1), true);"
Run-Psql "SELECT setval(pg_get_serial_sequence('producto','id_producto'), COALESCE((SELECT MAX(id_producto) FROM producto),1), true);"
Run-Psql "SELECT setval(pg_get_serial_sequence('pedidos','id_pedido'), COALESCE((SELECT MAX(id_pedido) FROM pedidos),1), true);"
Run-Psql "SELECT setval(pg_get_serial_sequence('detalle_pedido','id_detalle'), COALESCE((SELECT MAX(id_detalle) FROM detalle_pedido),1), true);"
Run-Psql "SELECT setval(pg_get_serial_sequence('promociones','id_promo'), COALESCE((SELECT MAX(id_promo) FROM promociones),1), true);"
Run-Psql "SELECT setval(pg_get_serial_sequence('pagos','id_pago'), COALESCE((SELECT MAX(id_pago) FROM pagos),1), true);"

Remove-Item Env:PGPASSWORD
