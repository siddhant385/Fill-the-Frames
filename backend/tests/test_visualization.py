import os
import tempfile
import pytest
import h5py
import netCDF4 as nc
import numpy as np
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.scientific.visualization_service import VisualizationService

client = TestClient(app)

@pytest.fixture
def mock_netcdf():
    fd, path = tempfile.mkstemp(suffix=".nc")
    os.close(fd)
    
    ds = nc.Dataset(path, 'w', format='NETCDF4')
    ds.createDimension('time', 2)
    ds.createDimension('lat', 10)
    ds.createDimension('lon', 10)
    
    times = ds.createVariable('time', 'f8', ('time',))
    lats = ds.createVariable('lat', 'f4', ('lat',))
    lons = ds.createVariable('lon', 'f4', ('lon',))
    temp = ds.createVariable('temperature', 'f4', ('time', 'lat', 'lon',))
    
    times[:] = [1620000000, 1620003600]
    lats[:] = np.linspace(-90, 90, 10)
    lons[:] = np.linspace(-180, 180, 10)
    temp[:] = np.random.uniform(200, 300, size=(2, 10, 10))
    
    ds.close()
    
    yield path
    os.remove(path)

@patch('app.services.scientific.visualization_service.VisualizationService._get_file_path')
def test_get_variables(mock_get_path, mock_netcdf):
    mock_get_path.return_value = mock_netcdf
    
    response = client.get("/api/v1/visualization/test_nc/variables")
    assert response.status_code == 200
    data = response.json()
    assert "variables" in data
    var_names = [v["name"] for v in data["variables"]]
    assert "temperature" in var_names
    
    # Check variable details
    temp_var = next(v for v in data["variables"] if v["name"] == "temperature")
    assert temp_var["shape"] == [2, 10, 10]

@patch('app.services.scientific.visualization_service.VisualizationService._get_file_path')
def test_get_frame_valid(mock_get_path, mock_netcdf):
    mock_get_path.return_value = mock_netcdf
    
    response = client.get("/api/v1/visualization/test_nc/frame?variable=temperature&time_index=0")
    assert response.status_code == 200
    data = response.json()
    assert data["variable"] == "temperature"
    assert data["time_index"] == 0
    assert data["shape"] == [10, 10]
    assert "z" in data
    assert len(data["z"]) == 10
    assert len(data["z"][0]) == 10
    
    # Check stats
    assert "min" in data
    assert "max" in data
    assert "mean" in data
    assert "std" in data
    assert data["min"] <= data["max"]
    assert data["std"] >= 0

@patch('app.services.scientific.visualization_service.VisualizationService._get_file_path')
def test_get_frame_invalid_variable(mock_get_path, mock_netcdf):
    mock_get_path.return_value = mock_netcdf
    
    response = client.get("/api/v1/visualization/test_nc/frame?variable=non_existent&time_index=0")
    assert response.status_code == 400
    assert "Invalid Variable" in response.json()["detail"]

@patch('app.services.scientific.visualization_service.VisualizationService._get_file_path')
def test_get_frame_invalid_time_index(mock_get_path, mock_netcdf):
    mock_get_path.return_value = mock_netcdf
    
    response = client.get("/api/v1/visualization/test_nc/frame?variable=temperature&time_index=999")
    assert response.status_code == 400
    assert "Invalid Time Index" in response.json()["detail"]

def test_get_frame_file_not_found():
    # Don't mock the get path, let it fail natively
    response = client.get("/api/v1/visualization/non_existent_file/frame?variable=temperature")
    assert response.status_code == 404
