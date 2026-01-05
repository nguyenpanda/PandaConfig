import re
from typing import Any, Callable
  

class ConfigResolver:
    
    var_pattern = re.compile(r'\$([a-zA-Z0-9_]+)')
    key_pattern = '${k}'
    
    def __init__(self, 
        raw_data: dict[str, Any], 
        config_func: dict[str, tuple[Callable, int]]
    ):
        self.data = raw_data
        self.config_func = config_func

    def resolve(self) -> dict[str, Any]:
        return self._resolve_dependencies(self.data, {}) # type: ignore
    
    def _split_args(self, text: str) -> list[str]:
        args, buffer = [], []
        depth = 0
        
        for char in text:
            if char == '(': depth += 1
            elif char == ')': depth -= 1
            
            if char == ' ' and depth == 0:
                if buffer:
                    args.append(''.join(buffer))
                    buffer = []
            else:
                buffer.append(char)
        
        if buffer:
            args.append(''.join(buffer))
            
        return args
    
    def _extract_balanced_func(self, text: str):
        start_idx = text.find('$(')
        if start_idx == -1:
            return None
        
        depth = 0
        content_start = start_idx + 2
        
        for i in range(content_start, len(text)):
            char = text[i]
            if char == '(':
                depth += 1
            elif char == ')':
                if depth == 0:
                    return text[start_idx:i+1].strip(), text[content_start:i].strip(), start_idx, i+1
                depth -= 1
        
        return None
    
    def _resolve_func(self, match: str, var: dict) -> Any:
        func_name, _, args = match.partition(' ')
            
        try:
            func, args_num = self.config_func[func_name]
        except KeyError:
            raise NameError(f'`{func_name}` is not define!')
        
        arg_list = self._split_args(args)
        if args_num != -1 and args_num != len(arg_list):
            raise TypeError(f'`{func_name}` takes {args_num} args, got {len(arg_list)}')
        arg_list = [self._resolve_dependencies(n, var) for n in arg_list]
        
        return func(*arg_list)
    
    def _resolve_dependencies(self, data: Any, var: dict):
        if isinstance(data, dict):
            for k, v in data.items():
                value = self._resolve_dependencies(v, var)
                var[self.key_pattern.format(k=k)] = value
                data[k] = value
            return data
        elif isinstance(data, list):
            return [self._resolve_dependencies(n, var) for n in data]
        elif isinstance(data, str):
            while True:
                match_info = self._extract_balanced_func(data)
                if not match_info:
                    break
                
                full_match, content, start, end = match_info
                result = self._resolve_func(content, var)
                
                if len(data) == len(full_match):
                    return result

                data = data[:start] + str(result) + data[end:]
                
            while True:
                match = self.var_pattern.search(data)
                if not match:
                    break
                
                full_match = match.group()
                if full_match not in var:
                    raise NameError(f'`{full_match}` is not defined in this scope!')

                val = var[full_match]
                if len(data) == len(full_match):
                    return val
                data = data.replace(full_match, str(val))
                
            return data
        else:
            return data
            
