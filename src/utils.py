from dataclasses import dataclass

@dataclass
class vec3:
    x: float
    y: float
    z: float

    def __getitem__(self, key: int) -> float:
        match key:
            case 0: return self.x
            case 1: return self.y
            case 2: return self.z
            case _: raise IndexError 

    def __setitem__(self, key: int, val: float) -> None:
        match key:
            case 0: self.x = val
            case 1: self.y = val
            case 2: self.z = val
            case _: raise IndexError 
    
    def __str__(self):
        return f"{self.x}i + {self.y}j + {self.z}k"
    
@dataclass
class vec3bool:
    x: bool
    y: bool
    z: bool

    def __getitem__(self, key: int) -> bool:
        match key:
            case 0: return self.x
            case 1: return self.y
            case 2: return self.z
            case _: raise IndexError 