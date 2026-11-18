$ErrorActionPreference = "Stop"

$workspaceRoot = "C:\Users\ralel\OneDrive\GitHub\VIS-NIR_Spec_Spring26"
$hostPcDir = Join-Path $workspaceRoot "docs\source\_static\diagrams\host_pc"
$embeddedDir = Join-Path $workspaceRoot "docs\source\_static\diagrams\embedded"

$v = New-Object -ComObject Visio.Application
$v.Visible = $false
$v.AlertResponse = 7

function Draw-Container {
    param($page, $x, $y, $w, $h, $title, $fillRgb, $strokeRgb, $titleColor="RGB(15, 23, 42)")
    $box = $page.DrawRectangle($x - $w/2, $y - $h/2, $x + $w/2, $y + $h/2)
    $box.Cells("Rounding").FormulaU = "0.25 in"
    $box.Cells("FillForegnd").FormulaU = $fillRgb
    $box.Cells("LineColor").FormulaU = $strokeRgb
    $box.Cells("LineWeight").FormulaU = "2.0 pt"
    
    $tH = 0.55
    $tY = $y + $h/2 - $tH/2 - 0.15
    $tBox = $page.DrawRectangle($x - $w/2 + 0.2, $tY - $tH/2, $x + $w/2 - 0.2, $tY + $tH/2)
    $tBox.Cells("FillPattern").FormulaU = "0"
    $tBox.Cells("LinePattern").FormulaU = "0"
    $tBox.Text = $title
    $tBox.CellsSRC(3, 0, 0).FormulaU = """Segoe UI"""
    $tBox.CellsSRC(3, 0, 1).FormulaU = $titleColor
    $tBox.CellsSRC(3, 0, 2).FormulaU = "1" # Bold
    $tBox.CellsSRC(3, 0, 7).FormulaU = "15 pt"
    $tBox.Cells("VerticalAlign").FormulaU = "1"
    
    return $box
}

function Draw-Node {
    param($page, $x, $y, $w, $h, $title, $body, $fillRgb, $strokeRgb)
    $box = $page.DrawRectangle($x - $w/2, $y - $h/2, $x + $w/2, $y + $h/2)
    $box.Cells("Rounding").FormulaU = "0.15 in"
    $box.Cells("FillForegnd").FormulaU = $fillRgb
    $box.Cells("LineColor").FormulaU = $strokeRgb
    $box.Cells("LineWeight").FormulaU = "1.5 pt"
    
    $titleH = 0.48
    if (-not $body) {
        $titleH = $h - 0.1
    }
    $tY = $y + $h/2 - $titleH/2 - 0.10
    $tBox = $page.DrawRectangle($x - $w/2 + 0.12, $tY - $titleH/2, $x + $w/2 - 0.12, $tY + $titleH/2)
    $tBox.Cells("FillPattern").FormulaU = "0"
    $tBox.Cells("LinePattern").FormulaU = "0"
    $tBox.Text = $title
    $tBox.CellsSRC(3, 0, 0).FormulaU = """Segoe UI"""
    $tBox.CellsSRC(3, 0, 1).FormulaU = "RGB(15, 23, 42)"
    $tBox.CellsSRC(3, 0, 2).FormulaU = "1" # Bold
    $tBox.CellsSRC(3, 0, 7).FormulaU = "13 pt"
    $tBox.Cells("VerticalAlign").FormulaU = "1"
    
    if ($body) {
        $bH = $h - $titleH - 0.20
        $bY = $y - $h/2 + $bH/2 + 0.08
        $bBox = $page.DrawRectangle($x - $w/2 + 0.12, $bY - $bH/2, $x + $w/2 - 0.12, $bY + $bH/2)
        $bBox.Cells("FillPattern").FormulaU = "0"
        $bBox.Cells("LinePattern").FormulaU = "0"
        $bBox.Text = $body
        $bBox.CellsSRC(3, 0, 0).FormulaU = """Segoe UI"""
        $bBox.CellsSRC(3, 0, 1).FormulaU = "RGB(45, 55, 72)"
        $bBox.CellsSRC(3, 0, 2).FormulaU = "0" # Regular
        $bBox.CellsSRC(3, 0, 7).FormulaU = "10.5 pt"
        $bBox.Cells("VerticalAlign").FormulaU = "1"
    }
    
    return $box
}

function Connect-Shapes {
    param($page, $s1, $s2, $label="", $color="RGB(70, 80, 95)", $weight="2.0 pt", $endArrow="13", $beginArrow="0")
    $conn = $page.Drop($v.ConnectorToolDataObject, 0, 0)
    $conn.Cells("EndArrow").FormulaU = $endArrow
    $conn.Cells("BeginArrow").FormulaU = $beginArrow
    $conn.Cells("LineWeight").FormulaU = $weight
    $conn.Cells("LineColor").FormulaU = $color
    $conn.Cells("BeginX").GlueTo($s1.Cells("PinX"))
    $conn.Cells("EndX").GlueTo($s2.Cells("PinX"))
    
    if ($label) {
        $conn.Text = $label
        $conn.CellsSRC(3, 0, 0).FormulaU = """Segoe UI"""
        $conn.CellsSRC(3, 0, 1).FormulaU = "RGB(20, 25, 35)"
        $conn.CellsSRC(3, 0, 2).FormulaU = "1" # Bold
        $conn.CellsSRC(3, 0, 7).FormulaU = "9.5 pt"
    }
    return $conn
}

# ==========================================================
# 1. MINIMALIST HOST PC SYSTEM OVERVIEW (TRUE ZERO CROSSINGS)
# ==========================================================
Write-Host "Building Zero-Crossing Minimalist Host PC Overview..."
$docHost = $v.Documents.Add("")
$pageHost = $docHost.Pages.Item(1)
$pageHost.Name = "Host PC Overview"
$pageHost.PageSheet.Cells("PageWidth").FormulaU = "24.0 in"
$pageHost.PageSheet.Cells("PageHeight").FormulaU = "13.5 in"

# Title Header
$titleH = $pageHost.DrawRectangle(1.0, 12.3, 23.0, 13.2)
$titleH.Cells("FillPattern").FormulaU = "0"
$titleH.Cells("LinePattern").FormulaU = "0"
$titleH.Text = "Host PC System Overview`nDecoupled 125 Hz Data Ingress, Calibration Pipeline, and 30 FPS Operator Application"
$titleH.CellsSRC(3, 0, 0).FormulaU = """Segoe UI"""
$titleH.CellsSRC(3, 0, 1).FormulaU = "RGB(15, 23, 42)"
$titleH.CellsSRC(3, 0, 2).FormulaU = "1"
$titleH.CellsSRC(3, 0, 7).FormulaU = "18 pt"
$titleH.Cells("VerticalAlign").FormulaU = "1"

# 3 Containers
$cHost1 = Draw-Container $pageHost 3.4 6.2 5.0 10.4 "Microcontroller (STM32F411)" "RGB(244, 246, 246)" "RGB(189, 195, 199)" "RGB(44, 62, 80)"
$nH_Stream = Draw-Node $pageHost 3.4 8.5 4.2 2.4 "125 Hz Measurement Stream" "7416-byte binary frames over USB CDC`n3694 raw 16-bit ADC sample array`nMonotonically incrementing frame IDs" "RGB(254, 249, 231)" "RGB(241, 196, 15)"
$nH_Cmd    = Draw-Node $pageHost 3.4 3.8 4.2 2.4 "Hardware Command Ingestion" "Ingests EXP:<us>, START, STOP, STATUS`nEnforces 8000 us integer divisor rule (<= 8ms)`nSynchronous reload at ICG frame boundary" "RGB(234, 237, 237)" "RGB(149, 165, 166)"

$cHost2 = Draw-Container $pageHost 11.2 6.2 8.6 10.4 "Background Operations (125 Hz Cadence)" "RGB(253, 242, 233)" "RGB(237, 187, 153)" "RGB(120, 45, 5)"
$nB_Ingress  = Draw-Node $pageHost 11.2 9.1 7.6 1.9 "Device Ingress & Serial Manager (packet_reader.py)" "Ring buffer boundary framing & 28-byte CCD1 header validation`nDispatches ASCII device commands & separates diagnostic lines`nStrips 32 dummy samples & reconstructs 3648 raw 16-bit counts" "RGB(254, 249, 231)" "RGB(241, 196, 15)"
$nB_Pipeline = Draw-Node $pageHost 11.2 6.2 7.6 2.4 "Primary Calibration Pipeline (pipeline.py)" "1. Dark / Baseline Correction: Tracks drift & subtracts master dark`n2. Responsivity Correction: Flat-field PRNU & relative QE (denom >= 1e-4)`n3. Wavelength Mapping: Evaluates cubic polynomial: lambda(i) (400 - 1000 nm)" "RGB(254, 249, 231)" "RGB(230, 126, 34)"
$nB_Storage  = Draw-Node $pageHost 11.2 3.3 7.6 1.9 "Dual-Mode Data Export (storage/)" "Mode 1: Lightweight in-memory CSV export (raw & calibrated)`nMode 2: High-speed dense binary capture directly to disk (zero drop)" "RGB(235, 245, 251)" "RGB(93, 173, 226)"

$cHost3 = Draw-Container $pageHost 19.4 6.2 6.0 10.4 "Operator Application (Kivy GUI)" "RGB(234, 242, 232)" "RGB(169, 223, 191)" "RGB(20, 90, 50)"
$nG_Controls = Draw-Node $pageHost 19.4 8.5 5.2 2.8 "Device Controls & Acquisition Setup" "COM port auto-detection & Connect/Disconnect`nExposure time slider: 10 us to 5 s (Divisor rule)`nStart / Stop streaming & Dark calibration wizard`nDispatches runtime commands to Serial Manager" "RGB(249, 252, 249)" "RGB(46, 204, 113)"
$nG_Plot     = Draw-Node $pageHost 19.4 3.8 5.2 2.8 "Real-Time Visualizations (30 FPS)" "Live 3648-point line spectrum plot (30 FPS)`nRolling waterfall spectrogram (256 bins)`nInteractive cursors: Peak wavelength, FWHM, SNR`nDecoupled cadence guarantees zero frame drops" "RGB(249, 252, 249)" "RGB(46, 204, 113)"

# Connectors for Host PC (Strictly ZERO intersections)
# Top Row: Commands & Streaming
$null = Connect-Shapes $pageHost $nH_Stream $nB_Ingress "7416-byte CCD1 Frames @ 125 Hz" "RGB(31, 97, 141)" "2.2 pt"
$null = Connect-Shapes $pageHost $nG_Controls $nB_Ingress "Device Commands (EXP, START)" "RGB(192, 57, 43)" "2.0 pt"
$null = Connect-Shapes $pageHost $nB_Ingress $nH_Cmd "ASCII Commands over USB" "RGB(192, 57, 43)" "2.0 pt"

# Middle & Bottom Rows: Clean downward and outward flow
$null = Connect-Shapes $pageHost $nB_Ingress $nB_Pipeline "3648 Raw Samples" "RGB(180, 120, 0)" "2.0 pt"
$null = Connect-Shapes $pageHost $nB_Pipeline $nG_Plot "Decoupled 30 FPS Render Feed" "RGB(39, 174, 96)" "2.2 pt"
$null = Connect-Shapes $pageHost $nB_Pipeline $nB_Storage "Calibrated Spectra & Raw Ground Truth" "RGB(31, 97, 141)" "2.0 pt"

$hostVsdx = Join-Path $hostPcDir "host_pc_system_overview.vsdx"
$hostPng = Join-Path $hostPcDir "system-overview.png"
$docHost.SaveAs($hostVsdx)
$pageHost.Export($hostPng)
$docHost.Saved = $true
$docHost.Close()
Write-Host "Updated Host PC overview at $hostPng"

# ==========================================================
# 2. MINIMALIST EMBEDDED SYSTEM OVERVIEW (TRUE ZERO CROSSINGS)
# ==========================================================
Write-Host "Building Zero-Crossing Minimalist Embedded Overview..."
$docEmb = $v.Documents.Add("")
$pageEmb = $docEmb.Pages.Item(1)
$pageEmb.Name = "Embedded Overview"
$pageEmb.PageSheet.Cells("PageWidth").FormulaU = "24.0 in"
$pageEmb.PageSheet.Cells("PageHeight").FormulaU = "13.5 in"

# Title Header
$titleE = $pageEmb.DrawRectangle(1.0, 12.3, 23.0, 13.2)
$titleE.Cells("FillPattern").FormulaU = "0"
$titleE.Cells("LinePattern").FormulaU = "0"
$titleE.Text = "Embedded System Overview`nSTM32F411 Microcontroller Real-Time Timing, ADC Digitization, and 125 Hz USB Transport"
$titleE.CellsSRC(3, 0, 0).FormulaU = """Segoe UI"""
$titleE.CellsSRC(3, 0, 1).FormulaU = "RGB(15, 23, 42)"
$titleE.CellsSRC(3, 0, 2).FormulaU = "1"
$titleE.CellsSRC(3, 0, 7).FormulaU = "18 pt"
$titleE.Cells("VerticalAlign").FormulaU = "1"

# 3 Containers
$cEmb1 = Draw-Container $pageEmb 3.4 6.2 5.0 10.4 "Linear CCD Sensor (TCD1304DG)" "RGB(254, 249, 231)" "RGB(245, 176, 65)" "RGB(125, 102, 8)"
$nE_Clocks = Draw-Node $pageEmb 3.4 8.5 4.2 2.4 "Driver Board & Clock Inputs" "phiM: 2.0 MHz master shift clock (50% duty)`nICG: 5.5 us integration clear gate (125 Hz)`nSH: Electronic shutter gate (10 us - 5 s)`nLevel shifting buffers & 3.3V power conditioning" "RGB(255, 253, 231)" "RGB(212, 172, 13)"
$nE_Array  = Draw-Node $pageEmb 3.4 3.8 4.2 2.4 "CCD Sensor Array & Video Output" "3648 effective active light-sensitive pixels`n32 leading shielded + 14 trailing dummy pixels`nOutputs analog video waveform (Vos) with troughs proportional to exposure" "RGB(252, 243, 207)" "RGB(243, 156, 18)"

$cEmb2 = Draw-Container $pageEmb 11.2 6.2 8.6 10.4 "STM32F411 Microcontroller Core" "RGB(242, 244, 244)" "RGB(189, 195, 199)" "RGB(44, 62, 80)"
$nE_Timers = Draw-Node $pageEmb 11.2 9.1 7.6 1.9 "Precision Waveform Timers (TIM1 - TIM4)" "TIM1 (2.0 MHz fM clock) | TIM2 (125 Hz ICG frame sync pulse)`nTIM3 (SH electronic shutter) | TIM4 (500 kHz ADC conversion trigger)`nMicrosecond timing determinism via NVIC priority arbitration" "RGB(255, 253, 231)" "RGB(241, 196, 15)"
$nE_ADC    = Draw-Node $pageEmb 11.2 6.2 7.6 2.2 "ADC1 Digitizer & Circular DMA Buffer" "12-bit SAR ADC samples Vos on TIM4 trigger with zero jitter`nDMA streams conversions directly into 4-slot circular SRAM pool`nPreserves all 3694 line samples in exact spatial acquisition order" "RGB(232, 248, 245)" "RGB(72, 201, 176)"
$nE_Comm   = Draw-Node $pageEmb 11.2 3.3 7.6 2.0 "Command Parser & Packetizer Engine" "Parses incoming ASCII command tokens (EXP:<us>, START, STOP)`nEnforces 8000 us integer divisors; reloads timers synchronously at ICG`nPackages 3694 samples into 7416-byte binary frames (28-byte CCD1 header)" "RGB(254, 245, 231)" "RGB(245, 205, 145)"

$cEmb3 = Draw-Container $pageEmb 19.4 6.2 6.0 10.4 "Host PC Wire Interface (USB CDC)" "RGB(235, 245, 251)" "RGB(133, 193, 233)" "RGB(31, 97, 141)"
$nE_HostCmd    = Draw-Node $pageEmb 19.4 8.5 5.2 2.8 "Host Command & Status Channel" "Host dispatches ASCII command strings: EXP:<us>\n`nControls acquisition lifecycle: START\n / STOP\n`nQueries device telemetry: STATUS\n`nZero silent frame truncation or loss" "RGB(234, 237, 237)" "RGB(149, 165, 166)"
$nE_HostStream = Draw-Node $pageEmb 19.4 3.8 5.2 2.8 "USB CDC Virtual COM Port" "USB 2.0 Full-Speed 12 Mbit/s wire transport`nTransmits 7416-byte CCD1 frames at 125 Hz`nMultiplexes ASCII diagnostic text lines`nDelivers VBUS 5V power to onboard 3.3V LDO" "RGB(232, 246, 243)" "RGB(72, 201, 176)"

# Connectors for Embedded (Strictly ZERO intersections)
$null = Connect-Shapes $pageEmb $nE_Timers $nE_Clocks "phiM (2 MHz), ICG & SH Pulses" "RGB(180, 120, 0)" "2.2 pt"
$null = Connect-Shapes $pageEmb $nE_Timers $nE_ADC "TIM4 500 kHz Sync" "RGB(120, 120, 120)" "1.6 pt"
$null = Connect-Shapes $pageEmb $nE_Array $nE_ADC "Vos Analog Video Waveform" "RGB(200, 75, 0)" "2.2 pt"
$null = Connect-Shapes $pageEmb $nE_ADC $nE_Comm "Committed 3694 Samples" "RGB(22, 160, 133)" "2.0 pt"
$null = Connect-Shapes $pageEmb $nE_HostCmd $nE_Timers "ASCII Commands (EXP, START)" "RGB(180, 40, 30)" "2.0 pt"
$null = Connect-Shapes $pageEmb $nE_Comm $nE_HostStream "7416-Byte CCD1 Frames @ 125 Hz" "RGB(35, 120, 175)" "2.2 pt"

$embVsdx = Join-Path $embeddedDir "embedded_system_overview.vsdx"
$embPng = Join-Path $embeddedDir "system-overview.png"
$docEmb.SaveAs($embVsdx)
$pageEmb.Export($embPng)
$docEmb.Saved = $true
$docEmb.Close()
Write-Host "Updated Embedded overview at $embPng"

$v.Quit()
Write-Host "Done!"
