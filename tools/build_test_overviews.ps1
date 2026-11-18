$ErrorActionPreference = "Stop"

$workspaceRoot = "C:\Users\ralel\OneDrive\GitHub\VIS-NIR_Spec_Spring26"
$hostPcDir = Join-Path $workspaceRoot "docs\source\_static\diagrams\host_pc"
$embeddedDir = Join-Path $workspaceRoot "docs\source\_static\diagrams\embedded"

$v = New-Object -ComObject Visio.Application
$v.Visible = $false
$v.AlertResponse = 7

function Draw-Container {
    param($page, $x, $y, $w, $h, $title, $fillRgb, $strokeRgb, $rounding="0.25 in", $titleColor="RGB(20, 30, 45)", $titleSize="14 pt")
    $box = $page.DrawRectangle($x - $w/2, $y - $h/2, $x + $w/2, $y + $h/2)
    $box.Cells("Rounding").FormulaU = $rounding
    $box.Cells("FillForegnd").FormulaU = $fillRgb
    $box.Cells("LineColor").FormulaU = $strokeRgb
    $box.Cells("LineWeight").FormulaU = "2.0 pt"
    
    $tH = 0.52
    $tY = $y + $h/2 - $tH/2 - 0.12
    $tBox = $page.DrawRectangle($x - $w/2 + 0.2, $tY - $tH/2, $x + $w/2 - 0.2, $tY + $tH/2)
    $tBox.Cells("FillPattern").FormulaU = "0"
    $tBox.Cells("LinePattern").FormulaU = "0"
    $tBox.Text = $title
    $tBox.CellsSRC(3, 0, 0).FormulaU = """Segoe UI"""
    $tBox.CellsSRC(3, 0, 1).FormulaU = $titleColor
    $tBox.CellsSRC(3, 0, 2).FormulaU = "1"
    $tBox.CellsSRC(3, 0, 7).FormulaU = $titleSize
    $tBox.Cells("VerticalAlign").FormulaU = "1"
    
    return $box
}

function Draw-Node {
    param($page, $x, $y, $w, $h, $title, $body, $fillRgb, $strokeRgb, $rounding="0.12 in", $titleSize="11 pt", $bodySize="9 pt")
    $box = $page.DrawRectangle($x - $w/2, $y - $h/2, $x + $w/2, $y + $h/2)
    $box.Cells("Rounding").FormulaU = $rounding
    $box.Cells("FillForegnd").FormulaU = $fillRgb
    $box.Cells("LineColor").FormulaU = $strokeRgb
    $box.Cells("LineWeight").FormulaU = "1.5 pt"
    
    $titleH = 0.44
    if (-not $body) {
        $titleH = $h - 0.1
    }
    $tY = $y + $h/2 - $titleH/2 - 0.08
    $tBox = $page.DrawRectangle($x - $w/2 + 0.1, $tY - $titleH/2, $x + $w/2 - 0.1, $tY + $titleH/2)
    $tBox.Cells("FillPattern").FormulaU = "0"
    $tBox.Cells("LinePattern").FormulaU = "0"
    $tBox.Text = $title
    $tBox.CellsSRC(3, 0, 0).FormulaU = """Segoe UI"""
    $tBox.CellsSRC(3, 0, 1).FormulaU = "RGB(15, 23, 42)"
    $tBox.CellsSRC(3, 0, 2).FormulaU = "1"
    $tBox.CellsSRC(3, 0, 7).FormulaU = $titleSize
    $tBox.Cells("VerticalAlign").FormulaU = "1"
    
    if ($body) {
        $bH = $h - $titleH - 0.16
        $bY = $y - $h/2 + $bH/2 + 0.08
        $bBox = $page.DrawRectangle($x - $w/2 + 0.1, $bY - $bH/2, $x + $w/2 - 0.1, $bY + $bH/2)
        $bBox.Cells("FillPattern").FormulaU = "0"
        $bBox.Cells("LinePattern").FormulaU = "0"
        $bBox.Text = $body
        $bBox.CellsSRC(3, 0, 0).FormulaU = """Segoe UI"""
        $bBox.CellsSRC(3, 0, 1).FormulaU = "RGB(40, 50, 65)"
        $bBox.CellsSRC(3, 0, 2).FormulaU = "0"
        $bBox.CellsSRC(3, 0, 7).FormulaU = $bodySize
        $bBox.Cells("VerticalAlign").FormulaU = "1"
    }
    
    return $box
}

function Connect-Shapes {
    param($page, $s1, $s2, $label="", $color="RGB(70, 75, 85)", $weight="1.6 pt", $endArrow="13", $beginArrow="0")
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
        $conn.CellsSRC(3, 0, 2).FormulaU = "1"
        $conn.CellsSRC(3, 0, 7).FormulaU = "8.5 pt"
    }
    return $conn
}

# ==========================================================
# 1. BUILD HOST PC SYSTEM OVERVIEW
# ==========================================================
Write-Host "Building Host PC System Overview..."
$docHost = $v.Documents.Add("")
$pageHost = $docHost.Pages.Item(1)
$pageHost.Name = "Host PC Overview"
$pageHost.PageSheet.Cells("PageWidth").FormulaU = "26.0 in"
$pageHost.PageSheet.Cells("PageHeight").FormulaU = "14.5 in"

# Title Header
$titleShape = $pageHost.DrawRectangle(1.0, 13.4, 25.0, 14.3)
$titleShape.Cells("FillPattern").FormulaU = "0"
$titleShape.Cells("LinePattern").FormulaU = "0"
$titleShape.Text = "Host PC Software Architecture & Decoupled Execution Model`n100% Data Capture Fidelity at 125 Hz Cadence Decoupled from 30 FPS Operator Application"
$titleShape.CellsSRC(3, 0, 0).FormulaU = """Segoe UI"""
$titleShape.CellsSRC(3, 0, 1).FormulaU = "RGB(15, 23, 42)"
$titleShape.CellsSRC(3, 0, 2).FormulaU = "1"
$titleShape.CellsSRC(3, 0, 7).FormulaU = "18 pt"
$titleShape.Cells("VerticalAlign").FormulaU = "1"

# Container 1 (Left): Microcontroller Interface
$cHost1 = Draw-Container $pageHost 3.2 7.0 4.8 11.8 "Microcontroller Interface (STM32F411)" "RGB(242, 244, 244)" "RGB(160, 170, 175)" "0.25 in" "RGB(30, 45, 60)" "13.5 pt"
$nH_1 = Draw-Node $pageHost 3.2 11.2 4.0 1.6 "Binary Frame Stream (125 Hz)" "7416-Byte CCD1 Packet Cadence`n3694 Total 16-Bit ADC Samples`n(32 Dummy + 3648 Active + 14 Dummy)" "RGB(254, 249, 231)" "RGB(212, 172, 13)"
$nH_2 = Draw-Node $pageHost 3.2 8.8 4.0 1.5 "USB CDC Virtual COM Port" "Full-Speed 12 Mbit/s Wire Transport`nBidirectional ASCII & Binary Framing" "RGB(235, 245, 251)" "RGB(93, 173, 226)"
$nH_3 = Draw-Node $pageHost 3.2 6.4 4.0 1.5 "ASCII Diagnostic Stream" "Multiplexed Text Telemetry`nHardware Status, Banners, Diagnostics" "RGB(254, 249, 231)" "RGB(212, 172, 13)"
$nH_4 = Draw-Node $pageHost 3.2 3.6 4.0 1.8 "MCU Command Ingestion" "Receives Host ASCII Commands:`nEXP:<us>, START, STOP, STATUS`nEnforces 8000 us Divisor Rule (<= 8ms)" "RGB(234, 237, 237)" "RGB(149, 165, 166)"

# Container 2 (Center): Background Operations
$cHost2 = Draw-Container $pageHost 11.8 7.0 10.4 11.8 "Background Operations (Decoupled 125 Hz Cadence)" "RGB(253, 242, 233)" "RGB(230, 175, 135)" "0.25 in" "RGB(120, 45, 5)" "14 pt"
$nB_1 = Draw-Node $pageHost 11.8 11.2 9.6 1.6 "Device Ingress & Packet Demuxing (packet_reader.py)" "Ring Buffer Boundary Synchronization | Validates 28-Byte CCD1 Header & Frame ID`nSeparates Diagnostic ASCII Lines | Strips 32 Dummy & Reconstructs 3648 Raw Samples" "RGB(254, 249, 231)" "RGB(212, 172, 13)"

# Sub-container: Primary Data Pipeline
$cPipe = Draw-Container $pageHost 11.8 7.7 9.8 4.2 "Primary Data Pipeline & Calibration (processing/pipeline.py)" "RGB(254, 237, 222)" "RGB(225, 115, 25)" "0.18 in" "RGB(130, 40, 0)" "12 pt"
$nP_1 = Draw-Node $pageHost 9.3 8.6 4.4 1.4 "Dark & Baseline Correction" "Optical Black Drift Tracking`nMaster Dark Frame Subtraction`nInversion to Positive Light Counts" "RGB(255, 253, 231)" "RGB(212, 172, 13)"
$nP_2 = Draw-Node $pageHost 14.3 8.6 4.4 1.4 "Spectral Corrections (PRNU & QE)" "Pixel Response Non-Uniformity (PRNU)`nRelative Quantum Efficiency Curve`nBounded Denominator: Denom >= 1e-4" "RGB(255, 253, 231)" "RGB(212, 172, 13)"
$nP_3 = Draw-Node $pageHost 9.3 6.6 4.4 1.4 "Wavelength Polynomial Mapping" "Evaluates: lambda(i) = c0 + c1*i + c2*i^2 + c3*i^3`nMaps 3648 Pixels to 400-1000 nm Range`nHg-Ar / Ne Spectral Line Traceability" "RGB(255, 253, 231)" "RGB(212, 172, 13)"
$nP_4 = Draw-Node $pageHost 14.3 6.6 4.4 1.4 "Calibration Profile Storage" "JSON Calibration Models on Disk`nMaster Dark Profiles & Wavelength Coeffs`nRuntime Calibration Manager State" "RGB(255, 253, 231)" "RGB(212, 172, 13)"

$nB_3 = Draw-Node $pageHost 11.8 4.3 9.6 1.4 "Core State & Session Coordination (core/state_manager.py)" "Thread-Safe State Snapshots | Monotonic Sequence Gap Tracking (Missed Frame Detection)`nCircular In-Memory Session Caching | Streaming Metrics (125 Hz Cadence, Ingress Latency)" "RGB(254, 249, 231)" "RGB(212, 172, 13)"
$nB_4 = Draw-Node $pageHost 11.8 2.2 9.6 1.6 "Storage & Dual-Mode Persistence (storage/)" "Mode 1: Lightweight In-Memory CSV Export (Raw ADC Counts & Calibrated Spectra)`nMode 2: High-Speed Dense Binary Capture Directly to Disk for Long Zero-Drop Campaigns" "RGB(235, 245, 251)" "RGB(93, 173, 226)"

# Container 3 (Right): Operator Desktop Application
$cHost3 = Draw-Container $pageHost 21.6 7.0 7.4 11.8 "Operator Desktop Application (Decoupled 30 FPS Cadence)" "RGB(234, 242, 232)" "RGB(155, 215, 175)" "0.25 in" "RGB(15, 80, 45)" "14 pt"
$nG_1 = Draw-Node $pageHost 21.6 11.2 6.6 1.6 "Real-Time Visualizations (30 FPS Kivy Engine)" "Live 3648-Point Spectrum Line Plot`nRolling 256-Bin Compressed Waterfall Spectrogram`nDecoupled Cadence Guarantees 0% Ingress Drops" "RGB(249, 252, 249)" "RGB(110, 210, 155)"
$nG_2 = Draw-Node $pageHost 21.6 8.9 6.6 1.4 "Interactive Analytical Cursors" "Peak Wavelength Tracking & Spectral Centroid`nFull-Width at Half-Maximum (FWHM) Estimation`nSignal-to-Noise Ratio (SNR) Monitoring" "RGB(255, 253, 231)" "RGB(212, 172, 13)"
$nG_3 = Draw-Node $pageHost 21.6 6.5 6.6 1.7 "Device Connection & Acquisition Controls" "Auto-Detect COM Port & Connect/Disconnect`nExposure Slider: 10 us to 5 s (Enforces Divisor Rule)`nAcquisition Start / Stop / Live Pause Controls" "RGB(249, 252, 249)" "RGB(110, 210, 155)"
$nG_4 = Draw-Node $pageHost 21.6 4.3 6.6 1.3 "Calibration & User Settings Manager" "Dark Acquisition Wizard & Calibration Verification`nLoad / Save JSON User Configuration Profiles" "RGB(249, 252, 249)" "RGB(110, 210, 155)"
$nG_5 = Draw-Node $pageHost 21.6 2.2 6.6 1.5 "Export Triggers & Session Status" "One-Click CSV Export Trigger`nDense Binary Disk Recording Toggle`nLive Performance Metrics (FPS, Frame Count, Gaps)" "RGB(249, 252, 249)" "RGB(110, 210, 155)"

# Connections for Host PC
$null = Connect-Shapes $pageHost $nH_1 $nB_1 "7416-Byte Frames @ 125 Hz" "RGB(31, 97, 141)" "2.0 pt"
$null = Connect-Shapes $pageHost $nH_3 $nB_1 "ASCII Diagnostics" "RGB(110, 110, 110)"
$null = Connect-Shapes $pageHost $nB_1 $nP_1 "3648 Raw Samples" "RGB(180, 120, 0)" "1.8 pt"
$null = Connect-Shapes $pageHost $nP_1 $nP_2 "Net Counts" "RGB(180, 120, 0)" "1.8 pt"
$null = Connect-Shapes $pageHost $nP_2 $nP_3 "Responsivity Corrected" "RGB(180, 120, 0)" "1.8 pt"
$null = Connect-Shapes $pageHost $nP_4 $nP_2 "" "RGB(150, 150, 150)" "1.0 pt"
$null = Connect-Shapes $pageHost $nP_3 $nB_3 "Calibrated Spectrum" "RGB(30, 130, 60)" "2.0 pt"
$null = Connect-Shapes $pageHost $nB_3 $nG_1 "30 FPS Decoupled Stream" "RGB(30, 130, 60)" "2.0 pt"
$null = Connect-Shapes $pageHost $nG_2 $nG_1 "" "RGB(150, 150, 150)" "1.0 pt"
$null = Connect-Shapes $pageHost $nG_3 $nH_4 "ASCII Commands (EXP, START)" "RGB(180, 40, 30)" "2.0 pt"
$null = Connect-Shapes $pageHost $nG_4 $nP_4 "Settings / Dark Profile" "RGB(100, 100, 100)"
$null = Connect-Shapes $pageHost $nG_5 $nB_4 "Export Trigger" "RGB(31, 97, 141)" "1.8 pt"
$null = Connect-Shapes $pageHost $nB_1 $nB_4 "Raw Ground Truth" "RGB(120, 120, 120)" "1.2 pt"

$hostVsdx = Join-Path $hostPcDir "host_pc_system_overview.vsdx"
$hostPng = Join-Path $hostPcDir "system-overview.png"
$docHost.SaveAs($hostVsdx)
$pageHost.Export($hostPng)
$docHost.Saved = $true
$docHost.Close()
Write-Host "Host PC overview updated at $hostPng"

# ==========================================================
# 2. BUILD EMBEDDED SYSTEM OVERVIEW (OPTIMIZED ALIGNMENT)
# ==========================================================
Write-Host "Building Embedded System Overview with horizontal aligned signals..."
$docEmb = $v.Documents.Add("")
$pageEmb = $docEmb.Pages.Item(1)
$pageEmb.Name = "Embedded Overview"
$pageEmb.PageSheet.Cells("PageWidth").FormulaU = "26.0 in"
$pageEmb.PageSheet.Cells("PageHeight").FormulaU = "14.5 in"

# Title Header
$titleEmb = $pageEmb.DrawRectangle(1.0, 13.4, 25.0, 14.3)
$titleEmb.Cells("FillPattern").FormulaU = "0"
$titleEmb.Cells("LinePattern").FormulaU = "0"
$titleEmb.Text = "Embedded System Architecture & Hardware Real-Time Execution Model`nMicrosecond Timing Determinism, ADC Digitization, Circular DMA Buffering, and 125 Hz USB CDC Wire Transport"
$titleEmb.CellsSRC(3, 0, 0).FormulaU = """Segoe UI"""
$titleEmb.CellsSRC(3, 0, 1).FormulaU = "RGB(15, 23, 42)"
$titleEmb.CellsSRC(3, 0, 2).FormulaU = "1"
$titleEmb.CellsSRC(3, 0, 7).FormulaU = "18 pt"
$titleEmb.Cells("VerticalAlign").FormulaU = "1"

# Container 1 (Left): Sensor & Driver Board Boundary
$cEmb1 = Draw-Container $pageEmb 3.2 7.0 4.8 11.8 "Sensor & Driver Board Boundary (TCD1304DG)" "RGB(254, 249, 231)" "RGB(240, 170, 50)" "0.25 in" "RGB(120, 95, 5)" "13.5 pt"
$nE_S1 = Draw-Node $pageEmb 3.2 11.2 4.0 1.6 "Toshiba TCD1304DG Sensor Array" "3694 Total Pixel Elements:`n* 32 Leading Dummy / Shielded Pixels`n* 3648 Effective Active Photodiode Array`n* 14 Trailing Dummy Pixels" "RGB(252, 243, 207)" "RGB(230, 145, 10)"
$nE_S2 = Draw-Node $pageEmb 3.2 8.6 4.0 1.6 "Digital Clock Inputs (phiM, ICG, SH)" "* phiM: 2.0 MHz Shift Clock (50% Duty)`n* ICG: Frame Clear Gate (5.5 us Low Pulse)`n* SH: Electronic Shutter (10 us - 5 s Pulse)`nStrict Microsecond Waveform Determinism" "RGB(255, 253, 231)" "RGB(212, 172, 13)"
$nE_S3 = Draw-Node $pageEmb 3.2 6.0 4.0 1.6 "Analog Video Output (Vos)" "Sequential Pixel Output Waveform`nTrough Voltages Proportional to Exposure`nLow-Impedance Drive to MCU ADC1 Pin`nSampled Synchronously by TIM4" "RGB(251, 238, 230)" "RGB(220, 140, 90)"
$nE_S4 = Draw-Node $pageEmb 3.2 3.4 4.0 1.6 "Driver Board Front-End" "High-Speed Logic Buffers & Level Shifting`nAnalog Video Pre-Conditioning Circuitry`nLow-Noise 3.3V Power Distribution" "RGB(252, 243, 207)" "RGB(230, 145, 10)"

# Container 2 (Center): STM32F411 Microcontroller Subsystem
$cEmb2 = Draw-Container $pageEmb 11.8 7.0 10.4 11.8 "STM32F411CEU6 Blackpill Microcontroller Core" "RGB(242, 244, 244)" "RGB(180, 185, 190)" "0.25 in" "RGB(40, 55, 70)" "14 pt"
$nE_M1 = Draw-Node $pageEmb 11.8 11.2 9.6 1.6 "System Control Logic & NVIC Priority Arbitration" "Clock Architecture (84/100 MHz SYSCLK, APB1/APB2 Timer Clocks)`nStrict Priority Arbitration: TIM1/TIM2 (Highest) > ADC1 > DMA Stream > USB FS Endpoint`nGuarantees Zero CPU Jitter on Critical Optical Waveform Generation" "RGB(234, 236, 238)" "RGB(125, 135, 145)"

# Sub-container: Timers, ADC & DMA
$cTimerSub = Draw-Container $pageEmb 11.8 7.7 9.8 4.2 "Precision Waveform Generation, Digitization & DMA Buffering" "RGB(235, 245, 251)" "RGB(120, 185, 225)" "0.18 in" "RGB(25, 85, 125)" "12 pt"
$nT_1 = Draw-Node $pageEmb 9.3 8.6 4.4 1.4 "TIM1: Master Clock (phiM)" "2.0 MHz Continuous Clock (50% Duty)`nDrives CCD Shift Register Pixel Transport`nMicrosecond Phase Coherence" "RGB(255, 253, 231)" "RGB(212, 172, 13)"
$nT_2 = Draw-Node $pageEmb 14.3 8.6 4.4 1.4 "TIM2 (ICG) & TIM3 (SH) Engine" "TIM2: 5.5 us Clear Gate Pulse (125 Hz Cadence)`nTIM3: Electronic Shutter (10 us - 5 s)`nSynchronous Reload on Frame Boundary" "RGB(255, 253, 231)" "RGB(212, 172, 13)"
$nT_3 = Draw-Node $pageEmb 9.3 6.6 4.4 1.4 "ADC1: Analog Digitization" "12-Bit Fast SAR ADC Sampling Vos`nTriggered on TIM4 Pixel Trough Sync`nDigitizes All 3694 Elements Sequentially" "RGB(232, 248, 245)" "RGB(100, 205, 185)"
$nT_4 = Draw-Node $pageEmb 14.3 6.6 4.4 1.4 "DMA1 Stream: Circular Buffer Pool" "Zero-CPU DMA Transfers to SRAM`n4-Slot Circular Frame Buffer Pool`nPreserves Exact Spatial Acquisition Sequence" "RGB(232, 248, 245)" "RGB(100, 205, 185)"

$nE_M3 = Draw-Node $pageEmb 11.8 4.3 9.6 1.4 "Command Parser & Schedule Reload Logic" "Ingests Host ASCII Tokens (EXP:<us>, START, STOP, STATUS)`nEnforces Valid Exposure Divisors (Exact Integer Divisors of 8000 us for <= 8 ms)`nSynchronously Updates Hardware Timer Reload Registers at Next ICG Transition" "RGB(254, 245, 231)" "RGB(245, 205, 145)"
$nE_M4 = Draw-Node $pageEmb 11.8 2.2 9.6 1.6 "USB CDC Transport & Binary Packetizer (CCD1)" "28-Byte Little-Endian Header: Magic CCD1 | Version 2 | 32-Bit Frame ID | Timestamp | Exp Time | Flags`n7392-Byte Payload: 3694 Digitized 16-Bit Samples (32 Dummy + 3648 Active + 14 Dummy) in Acquired Order`nFull-Speed USB 2.0 Bulk IN Transmission at 125 Hz Cadence | Monotonically Incrementing IDs" "RGB(235, 245, 251)" "RGB(115, 170, 205)"

# Container 3 (Right): Host PC Wire Boundary
$cEmb3 = Draw-Container $pageEmb 21.6 7.0 7.4 11.8 "Host PC Wire Interface (USB CDC Virtual COM)" "RGB(235, 245, 251)" "RGB(120, 185, 225)" "0.25 in" "RGB(25, 85, 125)" "14 pt"
$nE_P1 = Draw-Node $pageEmb 21.6 11.2 6.6 1.6 "USB-C Physical Bus & Power" "USB 2.0 Full-Speed 12 Mbit/s Transport`nVirtual COM Port (CDC ACM Protocol)`nVBUS 5V Power In -> Onboard 3.3V LDO" "RGB(232, 246, 243)" "RGB(65, 195, 170)"
$nE_P2 = Draw-Node $pageEmb 21.6 8.8 6.6 1.6 "ASCII Diagnostic Ingestion" "Host Reads Multiplexed Text Lines`nFirmware Version, Error Codes, Status Alerts`nPreserved in Diagnostic Event Log" "RGB(232, 246, 243)" "RGB(65, 195, 170)"
$nE_P3 = Draw-Node $pageEmb 21.6 6.3 6.6 1.5 "Host Command Transmission" "Host GUI Dispatches ASCII Command Strings:`nEXP:<us>\n (Sets Shutter Integration Time)`nSTART\n / STOP\n (Acquisition Lifecycle)`nSTATUS\n (Hardware Diagnostic Request)" "RGB(234, 237, 237)" "RGB(149, 165, 166)"
$nE_P4 = Draw-Node $pageEmb 21.6 2.2 6.6 1.6 "Binary Stream Ingestion (125 Hz)" "Host Serial Thread Reads 7416-Byte Frames`nZero Frame Truncation or Packet Corruption`nMonotonic Sequence Gap Monitoring" "RGB(232, 246, 243)" "RGB(65, 195, 170)"

# Connections for Embedded (Straight, Clean Horizontal Routing)
$null = Connect-Shapes $pageEmb $nT_1 $nE_S2 "phiM (2.0 MHz Clock)" "RGB(180, 120, 0)" "2.0 pt"
$null = Connect-Shapes $pageEmb $nT_2 $nE_S2 "ICG & SH Pulses" "RGB(180, 120, 0)" "1.8 pt"
$null = Connect-Shapes $pageEmb $nE_S3 $nT_3 "Vos Analog Troughs" "RGB(200, 75, 0)" "2.0 pt"
$null = Connect-Shapes $pageEmb $nT_1 $nT_3 "TIM4 Sync" "RGB(140, 140, 140)"
$null = Connect-Shapes $pageEmb $nT_3 $nT_4 "12-Bit Conversions" "RGB(18, 150, 125)" "1.8 pt"
$null = Connect-Shapes $pageEmb $nT_4 $nE_M4 "Committed 3694 Samples" "RGB(35, 120, 175)" "2.0 pt"
$null = Connect-Shapes $pageEmb $nE_M4 $nE_P4 "7416-Byte CCD1 Frames @ 125 Hz" "RGB(35, 120, 175)" "2.2 pt"
$null = Connect-Shapes $pageEmb $nE_M4 $nE_P2 "Diagnostics" "RGB(110, 110, 110)"
$null = Connect-Shapes $pageEmb $nE_P3 $nE_M3 "ASCII Commands (EXP, START)" "RGB(180, 40, 30)" "2.0 pt"
$null = Connect-Shapes $pageEmb $nE_M3 $nT_2 "Synchronous Reload @ ICG" "RGB(180, 120, 0)" "1.6 pt"
$null = Connect-Shapes $pageEmb $nE_M1 $nE_M4 "Status Flags & Header" "RGB(90, 90, 90)" "1.0 pt"

$embVsdx = Join-Path $embeddedDir "embedded_system_overview.vsdx"
$embPng = Join-Path $embeddedDir "system-overview.png"
$docEmb.SaveAs($embVsdx)
$pageEmb.Export($embPng)
$docEmb.Saved = $true
$docEmb.Close()
Write-Host "Embedded overview updated at $embPng"

$v.Quit()
Write-Host "Completed successfully!"
