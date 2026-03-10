$ErrorActionPreference = "Stop"
$backup = "db\software_de_oro_backup_2026-03-07.sql"
$lines = Get-Content $backup

function Get-CopyRows([string]$table) {
    $start = "COPY public.$table "
    $inBlock = $false
    $rows = New-Object System.Collections.Generic.List[string]
    foreach ($line in $lines) {
        if (-not $inBlock) {
            if ($line.StartsWith($start) -and $line.EndsWith(" FROM stdin;")) {
                $inBlock = $true
            }
            continue
        }
        if ($line -eq "\\.") { break }
        $rows.Add($line)
    }
    return $rows
}

function Write-RowsFile([string]$path, $rows) {
    [System.IO.File]::WriteAllLines($path, $rows, [System.Text.UTF8Encoding]::new($false))
}

$u = Get-CopyRows "usuarios"
$r = Get-CopyRows "registros"
$c = Get-CopyRows "categoria_producto"
$pr = Get-CopyRows "producto"
$pe = Get-CopyRows "pedidos"
$d = Get-CopyRows "detalle_pedido"
$pm = Get-CopyRows "promociones"
$pa = Get-CopyRows "pagos"

# producto en backup trae 10 columnas; la tabla actual tiene 8.
$pr8 = New-Object System.Collections.Generic.List[string]
foreach ($row in $pr) {
    if ([string]::IsNullOrWhiteSpace($row)) { continue }
    $parts = $row -split "`t", 10
    if ($parts.Length -ge 8) {
        $pr8.Add(($parts[0..7] -join "`t"))
    }
}

$tmp = ".tmp"
$uFile = Join-Path $tmp "usuarios.tsv"
$rFile = Join-Path $tmp "registros.tsv"
$cFile = Join-Path $tmp "categoria_producto.tsv"
$prFile = Join-Path $tmp "producto.tsv"
$peFile = Join-Path $tmp "pedidos.tsv"
$dFile = Join-Path $tmp "detalle_pedido.tsv"
$pmFile = Join-Path $tmp "promociones.tsv"
$paFile = Join-Path $tmp "pagos.tsv"

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

& $psql @dbArgs -c "TRUNCATE TABLE detalle_pedido, pagos, pedidos, producto, promociones, registros, categoria_producto, usuarios RESTART IDENTITY CASCADE;"

Get-Content $uFile | & $psql @dbArgs -c "COPY usuarios (id_usuario, nombre, email, password_hash, rol, estado, fecha_registro, email_verified, verification_code, verification_code_expiry) FROM STDIN;"
Get-Content $rFile | & $psql @dbArgs -c "COPY registros (id_registro, id_usuario, accion, fecha_accion) FROM STDIN;"
Get-Content $cFile | & $psql @dbArgs -c "COPY categoria_producto (id_categoria, nombre_categoria, descripcion) FROM STDIN;"
Get-Content $prFile | & $psql @dbArgs -c "COPY producto (id_producto, nombre, descripcion, precio, stock, id_categoria, imagen_url, eliminado) FROM STDIN;"
Get-Content $peFile | & $psql @dbArgs -c "COPY pedidos (id_pedido, id_usuario, fecha_pedido, estado) FROM STDIN;"
Get-Content $dFile | & $psql @dbArgs -c "COPY detalle_pedido (id_detalle, id_pedido, id_producto, cantidad, subtotal) FROM STDIN;"
Get-Content $pmFile | & $psql @dbArgs -c "COPY promociones (id_promo, nombre, descripcion, tipo_descuento, valor_descuento, codigo, fecha_inicio, fecha_fin, activo) FROM STDIN;"
Get-Content $paFile | & $psql @dbArgs -c "COPY pagos (id_pago, id_pedido, monto, metodo_pago, fecha_pago, estado_pago, id_promo, codigo_promo, tipo_descuento, valor_descuento, monto_descuento) FROM STDIN;"

& $psql @dbArgs -c "SELECT setval(pg_get_serial_sequence('usuarios','id_usuario'), COALESCE((SELECT MAX(id_usuario) FROM usuarios),1), true);"
& $psql @dbArgs -c "SELECT setval(pg_get_serial_sequence('categoria_producto','id_categoria'), COALESCE((SELECT MAX(id_categoria) FROM categoria_producto),1), true);"
& $psql @dbArgs -c "SELECT setval(pg_get_serial_sequence('producto','id_producto'), COALESCE((SELECT MAX(id_producto) FROM producto),1), true);"
& $psql @dbArgs -c "SELECT setval(pg_get_serial_sequence('pedidos','id_pedido'), COALESCE((SELECT MAX(id_pedido) FROM pedidos),1), true);"
& $psql @dbArgs -c "SELECT setval(pg_get_serial_sequence('detalle_pedido','id_detalle'), COALESCE((SELECT MAX(id_detalle) FROM detalle_pedido),1), true);"
& $psql @dbArgs -c "SELECT setval(pg_get_serial_sequence('promociones','id_promo'), COALESCE((SELECT MAX(id_promo) FROM promociones),1), true);"
& $psql @dbArgs -c "SELECT setval(pg_get_serial_sequence('pagos','id_pago'), COALESCE((SELECT MAX(id_pago) FROM pagos),1), true);"

Remove-Item Env:PGPASSWORD
