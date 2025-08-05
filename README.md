# Smoke Detection System - Brazil (SDB_p1_C)

A high-performance, real-time smoke detection system optimized with Numba for maximum CPU efficiency. This system processes multiple camera feeds simultaneously and provides a web-based dashboard for monitoring and control.

## 🚀 Features

### Core Functionality
- **Real-time Smoke Detection**: Advanced algorithms using Wasserstein distance and mean difference analysis
- **Multi-Camera Support**: Process up to 4 camera feeds simultaneously
- **Web Dashboard**: Real-time monitoring interface with video feeds and system status
- **Performance Optimized**: Numba JIT compilation for 2-4x speedup on CPU-intensive operations
- **Frame Processing Pipeline**: 7-stage processing (current, base, difference, wasserstein, mean, difference_wass, heatmap)

### Performance Optimizations
- **Numba JIT Compilation**: 1.85x speedup on core algorithms
- **Parallel Processing**: Multi-threaded frame processing
- **Memory Efficient**: Optimized frame buffers and data structures
- **CPU Reduction**: 40-60% reduction in CPU usage

## 📋 Requirements

### System Requirements
- **OS**: macOS, Linux, or Windows
- **Python**: 3.8+ (tested with Python 3.13)
- **RAM**: 4GB+ (8GB recommended)
- **CPU**: Multi-core processor (4+ cores recommended)
- **Storage**: 1GB+ free space

### Python Dependencies
```
opencv-python>=4.8.0
numpy>=1.24.0
flask>=2.3.0
pillow>=11.0.0
numba>=0.58.0
psutil>=5.9.0
firebase-admin>=7.0.0
```

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd SDB_p1_C
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Cameras
Edit `config/cameras.json` to configure your camera feeds:
```json
[
  {
    "id": 1,
    "name": "Camera 1",
    "ip": "192.168.1.100",
    "port": 554,
    "username": "admin",
    "password": "password",
    "enabled": true,
    "frame_width": 896,
    "frame_height": 504,
    "target_fps": 1.0
  }
]
```

### 5. Configure Settings
Edit `config/settings.json` to adjust system parameters:
```json
{
  "log_level": "DEBUG",
  "sleep_time": 1.0,
  "frame_width": 896,
  "frame_height": 504,
  "sliding_window": 16,
  "sensitivity": 5,
  "motion_threshold": 60,
  "detection_enabled": true
}
```

## 🚀 Usage

### Start the System
```bash
# Activate virtual environment
source venv/bin/activate

# Start the main application
python main.py
```

### Access the Dashboard
Open your web browser and navigate to:
```
http://localhost:5050
```

### Dashboard Features
- **Real-time Video Feeds**: View all camera feeds with different processing stages
- **System Status**: Monitor CPU usage, active cameras, and detection status
- **Settings Control**: Adjust detection parameters in real-time
- **Logs**: View system logs grouped by camera or type

## 📊 Performance Monitoring

### CPU Monitoring
```bash
# Monitor CPU usage
python logger/cpu_monitor.py

# Monitor system performance
python logger/performance_monitor.py
```

### Log Analysis
```bash
# View logs grouped by camera
python logger/log_viewer.py camera

# View smoke detection logs
python logger/log_viewer.py smoke

# Get system summary
python logger/log_viewer.py summary
```

## 🔧 Configuration

### Camera Configuration (`config/cameras.json`)
- **id**: Unique camera identifier
- **name**: Human-readable camera name
- **ip**: Camera IP address
- **port**: RTSP port (usually 554)
- **username/password**: Camera credentials
- **enabled**: Enable/disable camera
- **frame_width/height**: Processing resolution
- **target_fps**: Target frame rate

### System Settings (`config/settings.json`)
- **log_level**: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- **sleep_time**: Processing interval in seconds
- **frame_width/height**: Processing resolution
- **sliding_window**: Patch size for analysis
- **sensitivity**: Detection sensitivity threshold
- **motion_threshold**: Motion detection threshold
- **detection_enabled**: Enable/disable smoke detection

## 🏗️ Architecture

### Core Components

#### 1. Frame Processing Pipeline
```
Camera Feed → Frame Normalizer → Smoke Detector → Frame Buffer → Dashboard
```

#### 2. Numba Optimizations
- **Patch Utils**: Core mathematical operations (1.85x speedup)
- **Smoke Detector**: Frame comparison algorithms (2-3x speedup)
- **Grayscale Buffer**: Frame buffer operations (1.5-2x speedup)

#### 3. Processing Stages
1. **Current**: Latest frame from camera
2. **Base**: Reference frame for comparison
3. **Difference**: Frame difference analysis
4. **Wasserstein**: Wasserstein distance analysis
5. **Mean**: Mean difference analysis
6. **Difference_wass**: Wasserstein difference visualization
7. **Heatmap**: Detection heatmap visualization

### File Structure
```
SDB_p1_C/
├── main.py                          # Main application entry point
├── requirements.txt                 # Python dependencies
├── config/                          # Configuration files
│   ├── cameras.json                # Camera configuration
│   └── settings.json               # System settings
├── smoke/                          # Smoke detection algorithms
│   ├── smoke_detector.py           # Standard smoke detector
│   ├── smoke_detector_optimized.py # Numba-optimized detector
│   ├── patch_utils.py              # Standard patch utilities
│   ├── patch_utils_optimized.py    # Numba-optimized utilities
│   └── performance_test.py         # Performance testing
├── preprocessing/                   # Frame preprocessing
│   └── frame_normalizer.py         # Frame normalization and processing
├── processing/                      # Frame processing
│   ├── grayscale_buffer.py         # Standard grayscale buffer
│   └── grayscale_buffer_optimized.py # Numba-optimized buffer
├── dashboard/                       # Web dashboard
│   ├── app.py                      # Flask application
│   ├── routes/                     # API routes
│   ├── static/                     # Static files (CSS, JS, HTML)
│   └── templates/                  # HTML templates
├── logger/                         # Logging utilities
│   ├── log_manager.py              # Log management
│   ├── log_viewer.py               # Log viewing tools
│   └── cpu_monitor.py              # CPU monitoring
├── rtsp_stream/                    # RTSP stream handling
│   ├── rtsp_worker.py              # Individual camera worker
│   └── stream_manager.py           # Stream management
├── frame_buffer/                   # Frame buffer management
│   └── frame_buffer.py             # Frame storage and retrieval
└── logs/                           # System logs
    └── system.log                  # Main system log
```

## 🔍 Troubleshooting

### Common Issues

#### 1. High CPU Usage
- **Solution**: The system is designed to use multiple cores. Monitor with `python logger/cpu_monitor.py`
- **Expected**: 400-600% CPU usage is normal for 4-core systems

#### 2. Camera Connection Issues
- **Check**: Camera IP, credentials, and network connectivity
- **Verify**: RTSP stream is accessible with VLC or similar tool
- **Test**: Use test mode in camera configuration

#### 3. Dashboard Not Loading
- **Check**: Application is running on port 5050
- **Verify**: No firewall blocking the port
- **Test**: `curl http://localhost:5050/api/status`

#### 4. Numba Import Errors
- **Solution**: Ensure Numba is installed: `pip install "numba>=0.58.0"`
- **Fallback**: System automatically falls back to standard implementations

### Performance Tuning

#### 1. Reduce CPU Usage
- Increase `sleep_time` in settings
- Reduce `frame_width` and `frame_height`
- Lower `target_fps` in camera configuration

#### 2. Improve Detection Accuracy
- Adjust `sensitivity` and `motion_threshold`
- Fine-tune `sliding_window` size
- Monitor logs for detection patterns

#### 3. Optimize Memory Usage
- Reduce frame buffer size
- Lower processing resolution
- Monitor memory usage with `psutil`

## 📈 Performance Benchmarks

### Numba Optimizations Results
- **Patch Utils**: 1.85x speedup, 46% CPU reduction
- **Frame Comparisons**: 2-3x speedup
- **Overall System**: 2-4x speedup, 40-60% CPU reduction

### System Requirements
- **Minimum**: 4-core CPU, 4GB RAM
- **Recommended**: 8-core CPU, 8GB RAM
- **Optimal**: 16-core CPU, 16GB RAM

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `python smoke/performance_test.py`
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Add type hints where appropriate
- Include docstrings for all functions
- Test Numba optimizations before committing

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Getting Help
1. Check the troubleshooting section
2. Review system logs in `logs/system.log`
3. Monitor performance with provided tools
4. Create an issue with detailed error information

### Contact
- **Issues**: Use GitHub issues
- **Documentation**: Check this README and inline code comments
- **Performance**: Use provided monitoring tools

## 🔄 Updates

### Version History
- **v1.0**: Initial release with basic smoke detection
- **v1.1**: Added Numba optimizations
- **v1.2**: Enhanced dashboard and monitoring tools
- **v1.3**: Performance improvements and bug fixes

### Future Enhancements
- GPU acceleration with CUDA
- Machine learning-based detection
- Cloud integration
- Mobile app support
- Advanced analytics dashboard

---

**Note**: This system is optimized for real-time smoke detection in industrial environments. Ensure proper testing in your specific use case before deployment. 