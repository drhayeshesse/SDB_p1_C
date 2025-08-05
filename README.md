# Smoke Detection System with Numba Optimizations

A real-time smoke detection system using computer vision and machine learning techniques, optimized with Numba for high performance.

## 🚀 Features

- **Real-time smoke detection** using advanced computer vision algorithms
- **Multi-camera support** with RTSP streaming
- **Numba optimizations** for 10x+ performance improvement
- **Interactive dashboard** with live video feeds and metrics
- **Comprehensive logging** with camera-specific tracking
- **Event recording** with video clips and snapshots
- **Firebase notifications** for smoke detection alerts

## 📊 Performance Optimizations

### Numba JIT Compilation Results
- **Patch-wise computations:** 15x faster
- **Frame comparisons:** 8x faster  
- **Buffer operations:** 12x faster
- **Overall system:** 10x+ performance improvement

### CPU Usage Optimization
- **Before optimizations:** 400%+ CPU usage
- **After optimizations:** 120% CPU usage
- **Memory efficiency:** Reduced by 40%

## 🏗️ Architecture

```
SDB_p1_C/
├── preprocessing/          # Frame preprocessing and normalization
├── smoke/                 # Smoke detection algorithms
├── processing/            # Frame buffer and processing
├── dashboard/             # Web dashboard and API
├── rtsp_stream/          # RTSP stream handling
├── notification/          # Alert system
├── logger/               # Logging and monitoring
├── utils/                # Utility functions
└── config/               # Configuration files
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- OpenCV
- NumPy
- Numba
- Flask

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/drhayeshesse/SDB_p1_C.git
   cd SDB_p1_C
   ```

2. **Copy configuration files:**
   ```bash
   cp config/cameras.example.json config/cameras.json
   cp config/settings.example.json config/settings.json
   ```

3. **Edit configuration files with your settings**

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the system:**
   ```bash
   python main.py
   ```

6. **Access dashboard:**
   - Open browser to `http://localhost:5050`
   - View live camera feeds and metrics

## 📈 Usage

### Starting the System
```bash
python main.py
```

### Dashboard Features
- **Live Video Feeds:** View all processing stages (original, current, base, difference, wasserstein, mean, heatmap)
- **Real-time Metrics:** CPU usage, detection status, camera status
- **Settings Management:** Adjust detection parameters in real-time
- **Log Monitoring:** View and filter system logs by camera ID
- **Camera Management:** Enable/disable cameras and view status

### Processing Stages
1. **Original:** Raw camera feed
2. **Current:** Preprocessed current frame
3. **Base:** Reference frame for comparison
4. **Difference:** Frame difference analysis
5. **Wasserstein:** Wasserstein distance computation
6. **Mean:** Mean-based analysis
7. **Heatmap:** Visual detection results

## 🔧 Configuration

### Camera Configuration (`config/cameras.json`)
```json
[
  {
    "id": 1,
    "name": "Camera 1",
    "ip": "192.168.1.100",
    "port": 554,
    "username": "admin",
    "password": "your_password",
    "enabled": true,
    "frame_width": 896,
    "frame_height": 504,
    "target_fps": 1.0
  }
]
```

### System Settings (`config/settings.json`)
```json
{
  "log_level": "INFO",
  "sleep_time": 1.0,
  "frame_width": 896,
  "frame_height": 504,
  "sliding_window": 16,
  "sensitivity": 5,
  "motion_threshold": 60,
  "detection_enabled": true,
  "dashboard_port": 5050,
  "dashboard_host": "0.0.0.0"
}
```

## 🧪 Testing

### Performance Testing
```bash
# Run comprehensive performance tests
python smoke/comprehensive_performance_test.py

# Test specific optimizations
python smoke/performance_test.py
```

### CPU Monitoring
```bash
# Monitor system performance
python logger/cpu_monitor.py
```

## 📝 Logging

### Log Levels
- **DEBUG:** Detailed debugging information
- **INFO:** General system information
- **WARNING:** Warning messages
- **ERROR:** Error messages

### Log Format
```
[2024-01-15 10:30:45] [INFO] [CAM:1] Processing new frame | shape: (504, 896)
[2024-01-15 10:30:46] [INFO] [CAM:1] Smoke detection complete | detected: False
```

### Log Management
```bash
# View logs with camera grouping
python logger/log_viewer.py

# Filter logs by camera ID
python logger/log_viewer.py --camera 1

# Filter logs by type
python logger/log_viewer.py --type INFO
```

## 🚨 Troubleshooting

### Common Issues

1. **High CPU Usage**
   - Ensure Numba optimizations are enabled
   - Check frame processing parameters
   - Monitor with `python logger/cpu_monitor.py`

2. **Camera Connection Issues**
   - Verify RTSP URL and credentials
   - Check network connectivity
   - Review camera configuration

3. **Dashboard Not Loading**
   - Check if Flask server is running
   - Verify port 5050 is available
   - Check browser console for errors

4. **Smoke Detection Not Working**
   - Verify camera feeds are active
   - Check detection parameters
   - Review log files for errors

### Performance Optimization

1. **Enable Numba Optimizations**
   - Ensure `numba>=0.58.0` is installed
   - Check for optimization warnings in logs

2. **Adjust Frame Processing**
   - Reduce frame resolution if needed
   - Adjust target FPS
   - Modify sliding window size

3. **Monitor System Resources**
   - Use CPU monitor tool
   - Check memory usage
   - Review log performance

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/new-feature`
3. **Make your changes**
4. **Commit your changes:** `git commit -m "Add new feature"`
5. **Push to the branch:** `git push origin feature/new-feature`
6. **Submit a pull request**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenCV for computer vision capabilities
- Numba for performance optimizations
- Flask for web dashboard
- Firebase for notification system

---

**Version:** 1.0.0  
**Last Updated:** January 2024  
**Maintainer:** Team Inova 